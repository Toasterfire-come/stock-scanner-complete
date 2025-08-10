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
            <!-- Breaking News Banner -->
            <div class="breaking-news-section mb-6">
                <div class="breaking-news-banner">
                    <span class="breaking-label">🔴 BREAKING</span>
                    <div class="breaking-news-text" id="breaking-news-text">Loading latest breaking news...</div>
                </div>
            </div>

            <!-- News Filters Panel -->
            <div class="filters-card mb-6 p-6">
                <div class="panel-header">
                    <h3>🔍 Filter News</h3>
                    <div class="panel-actions">
                        <button id="clear-filters" class="btn btn-secondary">Clear Filters</button>
                    </div>
                </div>
                
                <div class="filter-controls" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-4); margin-top: var(--space-4);">
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
                    <div class="filter-group" style="display: flex; align-items: end;">
                        <button id="apply-filters" class="btn btn-primary" style="width: 100%;">Apply Filters</button>
                    </div>
                </div>
            </div>

            <!-- News Tabs -->
            <div class="card mb-6">
                <ul class="nav nav-tabs" id="news-tabs" role="tablist" style="display: flex; border-bottom: 2px solid var(--color-border); margin: 0; padding: 0; list-style: none; background: var(--color-surface);">
                    <li class="nav-item" role="presentation" style="margin: 0;">
                        <button class="tab-btn active" id="personalized-tab" data-bs-toggle="tab" data-bs-target="#personalized" type="button" role="tab">For You</button>
                    </li>
                    <li class="nav-item" role="presentation" style="margin: 0;">
                        <button class="tab-btn" id="business-tab" data-bs-toggle="tab" data-bs-target="#business" type="button" role="tab">Business</button>
                    </li>
                    <li class="nav-item" role="presentation" style="margin: 0;">
                        <button class="tab-btn" id="technology-tab" data-bs-toggle="tab" data-bs-target="#technology" type="button" role="tab">Technology</button>
                    </li>
                    <li class="nav-item" role="presentation" style="margin: 0;">
                        <button class="tab-btn" id="markets-tab" data-bs-toggle="tab" data-bs-target="#markets" type="button" role="tab">Markets</button>
                    </li>
                    <li class="nav-item" role="presentation" style="margin: 0;">
                        <button class="tab-btn" id="earnings-tab" data-bs-toggle="tab" data-bs-target="#earnings" type="button" role="tab">Earnings</button>
                    </li>
                </ul>

                <!-- Controls Header -->
                <div class="news-header p-6 pb-0">
                    <h2>📈 Latest News</h2>
                    <button id="refresh-news" class="btn btn-outline">🔄 Refresh</button>
                </div>

                <!-- Loading Indicator -->
                <div class="loading-indicator" id="news-loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading latest news...</p>
                </div>

                <!-- Tabbed News Feeds -->
                <div class="tab-content p-6" id="news-tab-content">
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

                <!-- Load More Section -->
                <div class="load-more-section p-6 pt-0" style="text-align: center;">
                    <button id="load-more-news" class="btn btn-secondary">Load More News</button>
                </div>
            </div>

            <!-- Trending Topics -->
            <div class="card p-6">
                <h3>🔥 Trending Topics</h3>
                <div id="trending-topics" class="trending-topics" style="display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-4);"></div>
            </div>
        </div>
    </div>
</div>

<style>
/* Additional styles for news page specific to unified theme */
.news-feed {
    display: grid;
    gap: var(--space-5);
}

.news-article {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.news-article:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.article-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-3);
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--color-border);
}

.article-category {
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 600;
}

.article-time {
    color: var(--color-text-muted);
    font-size: 0.875rem;
}

.article-title {
    color: var(--color-text);
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0 0 var(--space-3) 0;
    line-height: 1.3;
}

.article-title:hover {
    color: var(--color-primary);
    cursor: pointer;
}

.article-summary {
    color: var(--color-text-muted);
    line-height: 1.6;
    margin: 0 0 var(--space-4) 0;
}

.article-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
}

.article-source {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    font-weight: 500;
}

.article-symbols {
    display: flex;
    gap: var(--space-2);
}

.tab-pane {
    display: none;
}

.tab-pane.show.active {
    display: block;
}

.filter-group label {
    display: block;
    margin-bottom: var(--space-2);
    color: var(--color-text);
    font-weight: 600;
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
  const trendingTopics = document.getElementById('trending-topics');

  function renderArticles(container, items) {
    container.innerHTML = '';
    items.forEach(item => {
      const el = document.createElement('div');
      el.className = 'news-article';
      el.innerHTML = `
        <div class="article-header">
          <span class="article-category">${item.category}</span>
          <span class="article-time">${item.time}</span>
        </div>
        <h3 class="article-title">${item.title}</h3>
        <p class="article-summary">${item.summary}</p>
        <div class="article-footer">
          <span class="article-source">📰 ${item.source}</span>
          <div class="article-symbols">${(item.symbols||[]).map(s=>`<span class='symbol-tag'>${s}</span>`).join('')}</div>
        </div>
      `;
      container.appendChild(el);
    });
  }

  function renderTrendingTopics() {
    const topics = ['Market Rally', 'Tech Earnings', 'Fed Policy', 'Oil Prices', 'Crypto Surge', 'EV Stocks'];
    trendingTopics.innerHTML = topics.map(topic => 
      `<span class="trending-topic">${topic}</span>`
    ).join('');
  }

  function mock(category) {
    const base = ['business','technology','markets','earnings'];
    const cat = category === 'personalized' ? base[Math.floor(Math.random()*base.length)] : category;
    const templates = [
      { title: 'Market Opens Higher on Optimism', summary: 'Stocks rally amid positive macro data and earnings beats from major corporations.' },
      { title: 'Analysts Upgrade Major Tech Names', summary: 'Upgrades drive momentum in large-cap tech leaders as Q4 results exceed expectations.' },
      { title: 'Energy Stocks Gain on Supply Shift', summary: 'Commodity trends boost energy sector performance with oil prices climbing.' },
      { title: 'Banking Sector Shows Strength', summary: 'Financial institutions benefit from rising interest rate environment.' },
      { title: 'Healthcare Innovation Drives Growth', summary: 'Breakthrough treatments and medical technology advances fuel sector gains.' },
      { title: 'Consumer Spending Remains Robust', summary: 'Retail earnings showcase resilient consumer demand despite economic headwinds.' }
    ];
    const sources = ['Reuters','Bloomberg','MarketWatch','CNBC','Financial Times','Wall Street Journal'];
    const symbols = ['AAPL','MSFT','NVDA','AMZN','TSLA','GOOGL','META','JPM','JNJ','V'];
    return Array.from({length: 6}, (_, i) => {
      const t = templates[i % templates.length];
      return {
        category: cat.charAt(0).toUpperCase() + cat.slice(1),
        time: new Date(Date.now() - Math.random()*86400000).toLocaleTimeString(),
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

  function updateBreakingNews() {
    const breakingNews = [
      'Markets surge following positive economic data release',
      'Fed signals potential policy shift in upcoming meeting',
      'Major tech company announces significant acquisition',
      'Oil prices climb amid supply chain disruptions',
      'Bitcoin reaches new weekly high on institutional adoption'
    ];
    const randomNews = breakingNews[Math.floor(Math.random() * breakingNews.length)];
    document.getElementById('breaking-news-text').textContent = randomNews;
  }

  // Tab functionality
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      // Remove active class from all tabs and content
      document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.remove('show', 'active');
      });
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Show corresponding content
      const target = this.getAttribute('data-bs-target');
      const content = document.querySelector(target);
      if (content) {
        content.classList.add('show', 'active');
      }
      
      // Load feed for this tab
      const feedKey = target.substring(1);
      loadFeed(feedKey, false);
    });
  });

  // Initial loads
  Object.keys(feeds).forEach(k=>loadFeed(k));
  renderTrendingTopics();
  updateBreakingNews();

  document.getElementById('refresh-news').addEventListener('click', ()=>{
    const active = document.querySelector('.tab-btn.active');
    const target = active?.getAttribute('data-bs-target')?.substring(1) || 'personalized';
    loadFeed(target, true);
    updateBreakingNews();
  });

  document.getElementById('apply-filters').addEventListener('click', ()=>{
    const active = document.querySelector('.tab-btn.active');
    const target = active?.getAttribute('data-bs-target')?.substring(1) || 'personalized';
    loadFeed(target, true);
  });

  document.getElementById('clear-filters').addEventListener('click', ()=>{
    document.getElementById('news-category').value = 'all';
    document.getElementById('news-symbol').value = '';
    document.getElementById('news-timeframe').value = 'today';
  });

  document.getElementById('load-more-news').addEventListener('click', ()=>{
    const active = document.querySelector('.tab-btn.active');
    const target = active?.getAttribute('data-bs-target')?.substring(1) || 'personalized';
    const currentFeed = feeds[target];
    if (currentFeed) {
      const newArticles = mock(target);
      newArticles.forEach(item => {
        const el = document.createElement('div');
        el.className = 'news-article';
        el.innerHTML = `
          <div class="article-header">
            <span class="article-category">${item.category}</span>
            <span class="article-time">${item.time}</span>
          </div>
          <h3 class="article-title">${item.title}</h3>
          <p class="article-summary">${item.summary}</p>
          <div class="article-footer">
            <span class="article-source">📰 ${item.source}</span>
            <div class="article-symbols">${(item.symbols||[]).map(s=>`<span class='symbol-tag'>${s}</span>`).join('')}</div>
          </div>
        `;
        currentFeed.appendChild(el);
      });
    }
  });
});
</script>

<?php get_footer(); ?>