<?php
/**
 * Template Name: News
 * 
 * Market News with source filters, reading pane, and infinite scroll
 *
 * @package RetailTradeScanner
 */

get_header();

// News sources and categories
$news_sources = array(
    'all' => __('All Sources', 'retail-trade-scanner'),
    'reuters' => 'Reuters',
    'bloomberg' => 'Bloomberg',
    'cnbc' => 'CNBC',
    'wsj' => 'Wall Street Journal',
    'ft' => 'Financial Times',
    'marketwatch' => 'MarketWatch'
);

$news_categories = array(
    'all' => __('All Categories', 'retail-trade-scanner'),
    'markets' => __('Markets', 'retail-trade-scanner'),
    'stocks' => __('Stocks', 'retail-trade-scanner'),
    'crypto' => __('Cryptocurrency', 'retail-trade-scanner'),
    'earnings' => __('Earnings', 'retail-trade-scanner'),
    'economy' => __('Economy', 'retail-trade-scanner'),
    'politics' => __('Politics', 'retail-trade-scanner')
);

// Sample news data - in real implementation this would come from news API
$news_articles = array(
    array(
        'id' => 1,
        'title' => 'Apple Reports Strong Q4 Earnings, Stock Rises 5%',
        'excerpt' => 'Apple Inc. exceeded analyst expectations in its fourth quarter earnings report, driven by strong iPhone and services revenue...',
        'content' => 'Full article content would go here. Apple Inc. exceeded analyst expectations in its fourth quarter earnings report, driven by strong iPhone and services revenue. The tech giant reported earnings per share of $2.18 versus the expected $2.10, while revenue came in at $89.5 billion, beating estimates of $88.9 billion.',
        'source' => 'Reuters',
        'category' => 'earnings',
        'author' => 'Jane Smith',
        'published_time' => '2 hours ago',
        'published_date' => '2024-01-15',
        'image' => 'https://images.unsplash.com/photo-1611262588024-d12430b98920?w=300&h=200&fit=crop',
        'sentiment' => 'positive',
        'related_stocks' => array('AAPL'),
        'reading_time' => '3 min read'
    ),
    array(
        'id' => 2,
        'title' => 'Federal Reserve Signals Potential Rate Cut in March',
        'excerpt' => 'Fed Chairman Jerome Powell indicated that the central bank may consider lowering interest rates if inflation continues to decline...',
        'content' => 'Federal Reserve Chairman Jerome Powell indicated during his testimony before Congress that the central bank may consider lowering interest rates at the March meeting if inflation continues to decline as expected.',
        'source' => 'Bloomberg',
        'category' => 'economy',
        'author' => 'Michael Johnson',
        'published_time' => '4 hours ago',
        'published_date' => '2024-01-15',
        'image' => 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=200&fit=crop',
        'sentiment' => 'neutral',
        'related_stocks' => array(),
        'reading_time' => '5 min read'
    ),
    array(
        'id' => 3,
        'title' => 'Tesla Announces New Gigafactory in Southeast Asia',
        'excerpt' => 'Tesla Motors revealed plans for a new manufacturing facility in Vietnam, expected to produce 500,000 vehicles annually...',
        'content' => 'Tesla Motors has announced plans to build a new Gigafactory in Vietnam, which is expected to produce up to 500,000 vehicles annually once fully operational.',
        'source' => 'CNBC',
        'category' => 'stocks',
        'author' => 'Sarah Davis',
        'published_time' => '6 hours ago',
        'published_date' => '2024-01-15',
        'image' => 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=300&h=200&fit=crop',
        'sentiment' => 'positive',
        'related_stocks' => array('TSLA'),
        'reading_time' => '4 min read'
    )
);

$layout_args = array(
    'page_title' => __('Market News', 'retail-trade-scanner'),
    'page_description' => __('Stay updated with the latest financial news and market insights', 'retail-trade-scanner'),
    'page_class' => 'news-page',
    'header_actions' => array(
        array(
            'text' => __('Subscribe to Alerts', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'bell'
        ),
        array(
            'text' => __('Customize Feed', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'settings'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="news-layout grid grid-cols-12 gap-lg">
    
    <!-- News Filters Sidebar -->
    <div class="news-filters col-span-3">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Filters', 'retail-trade-scanner'); ?></h3>
                <button class="btn btn-ghost btn-sm clear-filters">
                    <?php esc_html_e('Clear', 'retail-trade-scanner'); ?>
                </button>
            </div>
            
            <div class="card-body">
                <form class="news-filter-form" id="news-filters">
                    
                    <!-- Sources Filter -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Sources', 'retail-trade-scanner'); ?></h4>
                        <div class="filter-options">
                            <?php foreach ($news_sources as $source_key => $source_name) : ?>
                                <label class="filter-option">
                                    <input type="checkbox" name="sources[]" value="<?php echo esc_attr($source_key); ?>" <?php echo $source_key === 'all' ? 'checked' : ''; ?>>
                                    <span class="checkmark"></span>
                                    <span class="option-label"><?php echo esc_html($source_name); ?></span>
                                </label>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <!-- Categories Filter -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Categories', 'retail-trade-scanner'); ?></h4>
                        <div class="filter-options">
                            <?php foreach ($news_categories as $category_key => $category_name) : ?>
                                <label class="filter-option">
                                    <input type="checkbox" name="categories[]" value="<?php echo esc_attr($category_key); ?>" <?php echo $category_key === 'all' ? 'checked' : ''; ?>>
                                    <span class="checkmark"></span>
                                    <span class="option-label"><?php echo esc_html($category_name); ?></span>
                                </label>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <!-- Sentiment Filter -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Sentiment', 'retail-trade-scanner'); ?></h4>
                        <div class="filter-options">
                            <label class="filter-option">
                                <input type="checkbox" name="sentiment[]" value="positive">
                                <span class="checkmark"></span>
                                <span class="option-label sentiment-positive"><?php esc_html_e('Positive', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="filter-option">
                                <input type="checkbox" name="sentiment[]" value="neutral">
                                <span class="checkmark"></span>
                                <span class="option-label sentiment-neutral"><?php esc_html_e('Neutral', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="filter-option">
                                <input type="checkbox" name="sentiment[]" value="negative">
                                <span class="checkmark"></span>
                                <span class="option-label sentiment-negative"><?php esc_html_e('Negative', 'retail-trade-scanner'); ?></span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Time Range Filter -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Time Range', 'retail-trade-scanner'); ?></h4>
                        <select class="form-select" name="time_range">
                            <option value="all"><?php esc_html_e('All Time', 'retail-trade-scanner'); ?></option>
                            <option value="1h"><?php esc_html_e('Last Hour', 'retail-trade-scanner'); ?></option>
                            <option value="24h" selected><?php esc_html_e('Last 24 Hours', 'retail-trade-scanner'); ?></option>
                            <option value="7d"><?php esc_html_e('Last Week', 'retail-trade-scanner'); ?></option>
                            <option value="30d"><?php esc_html_e('Last Month', 'retail-trade-scanner'); ?></option>
                        </select>
                    </div>
                    
                    <!-- Stock Symbol Filter -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Related Stocks', 'retail-trade-scanner'); ?></h4>
                        <input type="text" 
                               class="form-input" 
                               name="stock_filter" 
                               placeholder="<?php esc_attr_e('Enter symbol (e.g., AAPL)', 'retail-trade-scanner'); ?>"
                               autocomplete="off">
                        <div class="stock-suggestions hidden"></div>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Trending Topics -->
        <div class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Trending Topics', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <div class="trending-topics">
                    <button class="topic-tag">#FedRate</button>
                    <button class="topic-tag">#Earnings</button>
                    <button class="topic-tag">#TechStocks</button>
                    <button class="topic-tag">#AI</button>
                    <button class="topic-tag">#Crypto</button>
                    <button class="topic-tag">#Inflation</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- News Feed -->
    <div class="news-content col-span-6">
        <!-- Feed Header -->
        <div class="news-feed-header flex items-center justify-between mb-lg">
            <div class="feed-info">
                <h3><?php esc_html_e('Latest News', 'retail-trade-scanner'); ?></h3>
                <p class="text-sm text-muted">
                    <?php esc_html_e('Updated:', 'retail-trade-scanner'); ?> <span class="last-updated">2:45 PM</span>
                </p>
            </div>
            
            <div class="feed-controls">
                <div class="view-toggle">
                    <button class="view-btn active" data-view="card" title="<?php esc_attr_e('Card View', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('grid', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <button class="view-btn" data-view="list" title="<?php esc_attr_e('List View', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('list', ['width' => '16', 'height' => '16']); ?>
                    </button>
                </div>
                
                <button class="btn btn-ghost btn-sm auto-refresh-toggle">
                    <?php echo rts_get_icon('refresh', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Auto Refresh', 'retail-trade-scanner'); ?>
                </button>
            </div>
        </div>
        
        <!-- News Articles -->
        <div class="news-feed" id="news-feed">
            <?php foreach ($news_articles as $article) : ?>
                <article class="news-article card animate-scale-in" data-article-id="<?php echo esc_attr($article['id']); ?>">
                    
                    <?php if ($article['image']) : ?>
                        <div class="article-image">
                            <img src="<?php echo esc_url($article['image']); ?>" 
                                 alt="<?php echo esc_attr($article['title']); ?>"
                                 loading="lazy">
                            
                            <?php if ($article['sentiment']) : ?>
                                <div class="sentiment-indicator sentiment-<?php echo esc_attr($article['sentiment']); ?>">
                                    <?php
                                    $sentiment_icons = array(
                                        'positive' => 'trending-up',
                                        'negative' => 'trending-down',
                                        'neutral' => 'minus'
                                    );
                                    echo rts_get_icon($sentiment_icons[$article['sentiment']], ['width' => '16', 'height' => '16']);
                                    ?>
                                </div>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                    
                    <div class="article-content">
                        <div class="article-meta">
                            <span class="article-source"><?php echo esc_html($article['source']); ?></span>
                            <span class="meta-separator">•</span>
                            <time class="article-time" datetime="<?php echo esc_attr($article['published_date']); ?>">
                                <?php echo esc_html($article['published_time']); ?>
                            </time>
                            <span class="meta-separator">•</span>
                            <span class="reading-time"><?php echo esc_html($article['reading_time']); ?></span>
                            
                            <?php if (!empty($article['related_stocks'])) : ?>
                                <div class="related-stocks">
                                    <?php foreach ($article['related_stocks'] as $stock) : ?>
                                        <span class="stock-tag"><?php echo esc_html($stock); ?></span>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>
                        </div>
                        
                        <h2 class="article-title">
                            <a href="#" class="article-link" data-article="<?php echo esc_attr($article['id']); ?>">
                                <?php echo esc_html($article['title']); ?>
                            </a>
                        </h2>
                        
                        <p class="article-excerpt">
                            <?php echo esc_html($article['excerpt']); ?>
                        </p>
                        
                        <div class="article-actions">
                            <button class="action-btn" data-action="like" title="<?php esc_attr_e('Like', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('heart', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            
                            <button class="action-btn" data-action="bookmark" title="<?php esc_attr_e('Bookmark', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('bookmark', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            
                            <button class="action-btn" data-action="share" title="<?php esc_attr_e('Share', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('share', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            
                            <div class="article-category">
                                <?php
                                get_template_part('template-parts/components/badge', null, array(
                                    'value' => ucfirst($article['category']),
                                    'type' => 'neutral',
                                    'size' => 'xs'
                                ));
                                ?>
                            </div>
                        </div>
                    </div>
                </article>
            <?php endforeach; ?>
            
            <!-- Loading indicator for infinite scroll -->
            <div class="loading-indicator hidden">
                <div class="loading-spinner"></div>
                <p><?php esc_html_e('Loading more articles...', 'retail-trade-scanner'); ?></p>
            </div>
        </div>
        
        <!-- Load More Button -->
        <div class="load-more-container text-center mt-lg">
            <button class="btn btn-outline load-more-btn">
                <?php esc_html_e('Load More Articles', 'retail-trade-scanner'); ?>
                <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
            </button>
        </div>
    </div>
    
    <!-- Reading Pane -->
    <div class="news-reading-pane col-span-3">
        <div class="reading-pane-container">
            <div class="reading-pane-header">
                <h3><?php esc_html_e('Reading Pane', 'retail-trade-scanner'); ?></h3>
                <button class="close-reading-pane btn-ghost btn-sm">
                    <?php echo rts_get_icon('x', ['width' => '16', 'height' => '16']); ?>
                </button>
            </div>
            
            <div class="reading-pane-content">
                <div class="reading-pane-placeholder">
                    <?php echo rts_get_icon('newspaper', ['width' => '64', 'height' => '64', 'class' => 'placeholder-icon']); ?>
                    <p><?php esc_html_e('Select an article to read', 'retail-trade-scanner'); ?></p>
                    <small><?php esc_html_e('Click on any article title to view the full content here', 'retail-trade-scanner'); ?></small>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initNewsPage();
});

function initNewsPage() {
    const newsFilters = document.getElementById('news-filters');
    const newsFeed = document.getElementById('news-feed');
    const readingPane = document.querySelector('.reading-pane-content');
    const clearFiltersBtn = document.querySelector('.clear-filters');
    const loadMoreBtn = document.querySelector('.load-more-btn');
    const autoRefreshToggle = document.querySelector('.auto-refresh-toggle');
    
    let autoRefreshInterval = null;
    
    // Filter functionality
    if (newsFilters) {
        newsFilters.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            clearAllFilters();
        });
    }
    
    // Article selection
    newsFeed.addEventListener('click', function(e) {
        const articleLink = e.target.closest('.article-link');
        if (articleLink) {
            e.preventDefault();
            const articleId = articleLink.dataset.article;
            loadArticleInReadingPane(articleId);
        }
        
        // Action buttons
        const actionBtn = e.target.closest('.action-btn');
        if (actionBtn) {
            const action = actionBtn.dataset.action;
            const articleId = actionBtn.closest('.news-article').dataset.articleId;
            handleArticleAction(action, articleId, actionBtn);
        }
    });
    
    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            newsFeed.className = `news-feed view-${view}`;
        });
    });
    
    // Load more functionality
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            loadMoreArticles();
        });
    }
    
    // Auto refresh toggle
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('click', function() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                this.classList.remove('active');
                RTS.showInfo('Auto-refresh disabled');
            } else {
                autoRefreshInterval = setInterval(refreshNews, 60000); // 1 minute
                this.classList.add('active');
                RTS.showSuccess('Auto-refresh enabled (1 min)');
            }
        });
    }
    
    // Trending topics
    document.querySelectorAll('.topic-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const topic = this.textContent.replace('#', '');
            applyTopicFilter(topic);
        });
    });
    
    // Close reading pane
    const closeReadingPane = document.querySelector('.close-reading-pane');
    if (closeReadingPane) {
        closeReadingPane.addEventListener('click', function() {
            closeReadingPaneView();
        });
    }
    
    // Stock symbol autocomplete
    const stockFilter = document.querySelector('input[name="stock_filter"]');
    if (stockFilter) {
        stockFilter.addEventListener('input', function() {
            const query = this.value;
            if (query.length >= 2) {
                showStockSuggestions(query);
            } else {
                hideStockSuggestions();
            }
        });
    }
    
    // Initialize infinite scroll
    initInfiniteScroll();
    
    function applyFilters() {
        const formData = new FormData(newsFilters);
        const filters = {
            sources: formData.getAll('sources[]'),
            categories: formData.getAll('categories[]'),
            sentiment: formData.getAll('sentiment[]'),
            time_range: formData.get('time_range'),
            stock_filter: formData.get('stock_filter')
        };
        
        console.log('Applying filters:', filters);
        
        // Show loading
        showLoadingIndicator();
        
        // Simulate API call
        setTimeout(() => {
            hideLoadingIndicator();
            // Filter articles would be implemented here
            updateLastUpdatedTime();
        }, 1000);
    }
    
    function clearAllFilters() {
        newsFilters.reset();
        
        // Check "All" options
        document.querySelector('input[value="all"][name="sources[]"]').checked = true;
        document.querySelector('input[value="all"][name="categories[]"]').checked = true;
        
        applyFilters();
    }
    
    function loadArticleInReadingPane(articleId) {
        // Find article data (in real implementation, this would fetch from API)
        const articles = <?php echo json_encode($news_articles); ?>;
        const article = articles.find(a => a.id == articleId);
        
        if (!article) return;
        
        readingPane.innerHTML = `
            <div class="reading-article">
                <div class="reading-header">
                    <div class="reading-meta">
                        <span class="reading-source">${article.source}</span>
                        <span class="meta-separator">•</span>
                        <time class="reading-time">${article.published_time}</time>
                        <span class="meta-separator">•</span>
                        <span class="reading-duration">${article.reading_time}</span>
                    </div>
                    
                    <h1 class="reading-title">${article.title}</h1>
                    
                    <div class="reading-author">
                        By ${article.author}
                    </div>
                </div>
                
                ${article.image ? `
                    <div class="reading-image">
                        <img src="${article.image}" alt="${article.title}" />
                    </div>
                ` : ''}
                
                <div class="reading-content">
                    <p class="reading-excerpt">${article.excerpt}</p>
                    <div class="reading-body">
                        <p>${article.content}</p>
                    </div>
                </div>
                
                <div class="reading-footer">
                    <div class="reading-actions">
                        <button class="reading-action-btn" data-action="like">
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                            </svg>
                            Like
                        </button>
                        
                        <button class="reading-action-btn" data-action="share">
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"/>
                            </svg>
                            Share
                        </button>
                        
                        <button class="reading-action-btn" data-action="bookmark">
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
                            </svg>
                            Bookmark
                        </button>
                    </div>
                    
                    ${article.related_stocks && article.related_stocks.length ? `
                        <div class="related-stocks-section">
                            <h4>Related Stocks</h4>
                            <div class="related-stocks-list">
                                ${article.related_stocks.map(stock => `
                                    <a href="#" class="related-stock-link">${stock}</a>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Mark article as active
        document.querySelectorAll('.news-article').forEach(a => a.classList.remove('active'));
        document.querySelector(`[data-article-id="${articleId}"]`).classList.add('active');
    }
    
    function handleArticleAction(action, articleId, button) {
        switch (action) {
            case 'like':
                button.classList.toggle('active');
                console.log('Liked article:', articleId);
                break;
            case 'bookmark':
                button.classList.toggle('active');
                console.log('Bookmarked article:', articleId);
                RTS.showSuccess('Article bookmarked');
                break;
            case 'share':
                console.log('Sharing article:', articleId);
                if (navigator.share) {
                    navigator.share({
                        title: 'Market News Article',
                        url: window.location.href
                    });
                } else {
                    RTS.showInfo('Share functionality would open here');
                }
                break;
        }
    }
    
    function loadMoreArticles() {
        loadMoreBtn.disabled = true;
        loadMoreBtn.textContent = 'Loading...';
        
        // Simulate loading
        setTimeout(() => {
            loadMoreBtn.disabled = false;
            loadMoreBtn.innerHTML = 'Load More Articles <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>';
            
            RTS.showSuccess('New articles loaded');
        }, 2000);
    }
    
    function refreshNews() {
        updateLastUpdatedTime();
        console.log('Auto-refreshing news...');
    }
    
    function updateLastUpdatedTime() {
        const lastUpdated = document.querySelector('.last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date().toLocaleTimeString();
        }
    }
    
    function showLoadingIndicator() {
        document.querySelector('.loading-indicator').classList.remove('hidden');
    }
    
    function hideLoadingIndicator() {
        document.querySelector('.loading-indicator').classList.add('hidden');
    }
    
    function closeReadingPaneView() {
        readingPane.innerHTML = `
            <div class="reading-pane-placeholder">
                <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="placeholder-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                </svg>
                <p>Select an article to read</p>
                <small>Click on any article title to view the full content here</small>
            </div>
        `;
        
        document.querySelectorAll('.news-article').forEach(a => a.classList.remove('active'));
    }
    
    function initInfiniteScroll() {
        // Infinite scroll implementation would go here
        console.log('Infinite scroll initialized');
    }
    
    function applyTopicFilter(topic) {
        console.log('Filtering by topic:', topic);
        // Apply topic filter logic
    }
    
    function showStockSuggestions(query) {
        // Show stock symbol suggestions
        console.log('Showing suggestions for:', query);
    }
    
    function hideStockSuggestions() {
        document.querySelector('.stock-suggestions').classList.add('hidden');
    }
}
</script>

<style>
/* News Page Styles */
.news-layout {
    margin-bottom: var(--spacing-2xl);
}

.news-filters {
    position: sticky;
    top: calc(var(--header-height, 72px) + var(--spacing-lg));
    align-self: flex-start;
    max-height: calc(100vh - var(--header-height, 72px) - var(--spacing-2xl));
    overflow-y: auto;
}

.filter-group {
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-group:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.filter-group-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
    margin: 0 0 var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.filter-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.filter-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    font-size: var(--text-sm);
    color: var(--gray-700);
    transition: color var(--transition-fast) var(--easing-standard);
}

.filter-option:hover {
    color: var(--primary-600);
}

.filter-option input[type="checkbox"] {
    display: none;
}

.checkmark {
    width: 16px;
    height: 16px;
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-sm);
    position: relative;
    transition: all var(--transition-fast) var(--easing-standard);
}

.filter-option input:checked + .checkmark {
    background: var(--primary-500);
    border-color: var(--primary-500);
}

.filter-option input:checked + .checkmark::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 5px;
    width: 4px;
    height: 8px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}

.sentiment-positive {
    color: var(--success);
}

.sentiment-neutral {
    color: var(--gray-500);
}

.sentiment-negative {
    color: var(--danger);
}

.trending-topics {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.topic-tag {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(var(--primary-500), 0.1);
    border: 1px solid rgba(var(--primary-500), 0.2);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    color: var(--primary-600);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.topic-tag:hover {
    background: var(--primary-500);
    color: white;
}

.news-feed-header {
    padding: var(--spacing-lg) 0;
}

.feed-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.view-toggle {
    display: flex;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.view-btn {
    padding: var(--spacing-sm);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.view-btn.active {
    background: var(--primary-500);
    color: white;
}

.news-feed {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.news-feed.view-list .news-article {
    display: flex;
    flex-direction: row;
    gap: var(--spacing-md);
}

.news-feed.view-list .article-image {
    width: 120px;
    flex-shrink: 0;
}

.news-article {
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: all var(--transition-normal) var(--easing-standard);
}

.news-article:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.news-article.active {
    border: 2px solid var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

.article-image {
    position: relative;
    aspect-ratio: 16/9;
    overflow: hidden;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.article-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform var(--transition-slow) var(--easing-standard);
}

.news-article:hover .article-image img {
    transform: scale(1.05);
}

.sentiment-indicator {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.sentiment-indicator.sentiment-positive {
    background: var(--success);
}

.sentiment-indicator.sentiment-negative {
    background: var(--danger);
}

.sentiment-indicator.sentiment-neutral {
    background: var(--gray-500);
}

.article-content {
    padding: var(--spacing-lg);
}

.article-meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.article-source {
    font-weight: 600;
    color: var(--primary-600);
}

.meta-separator {
    color: var(--gray-300);
}

.related-stocks {
    display: flex;
    gap: var(--spacing-xs);
    margin-left: auto;
}

.stock-tag {
    padding: 2px var(--spacing-xs);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-sm);
    font-size: 10px;
    font-weight: 600;
}

.article-title {
    margin: 0 0 var(--spacing-sm);
    font-size: var(--text-lg);
    font-weight: 700;
    line-height: 1.3;
}

.article-link {
    color: inherit;
    text-decoration: none;
    transition: color var(--transition-fast) var(--easing-standard);
}

.article-link:hover {
    color: var(--primary-600);
    text-decoration: none;
}

.article-excerpt {
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--spacing-md);
}

.article-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.action-btn {
    padding: var(--spacing-xs);
    background: transparent;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    color: var(--gray-500);
}

.action-btn:hover,
.action-btn.active {
    color: var(--primary-600);
    border-color: var(--primary-600);
}

.loading-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-xl);
    color: var(--gray-500);
}

.auto-refresh-toggle.active {
    background: var(--success);
    color: white;
}

/* Reading Pane Styles */
.news-reading-pane {
    position: sticky;
    top: calc(var(--header-height, 72px) + var(--spacing-lg));
    align-self: flex-start;
    max-height: calc(100vh - var(--header-height, 72px) - var(--spacing-2xl));
}

.reading-pane-container {
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.reading-pane-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.reading-pane-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-lg);
}

.reading-pane-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: var(--gray-400);
    gap: var(--spacing-md);
}

.placeholder-icon {
    opacity: 0.5;
}

.reading-article {
    height: 100%;
}

.reading-header {
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
}

.reading-meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin-bottom: var(--spacing-md);
}

.reading-title {
    font-size: var(--text-xl);
    font-weight: 700;
    line-height: 1.3;
    margin: 0 0 var(--spacing-sm);
}

.reading-author {
    font-size: var(--text-sm);
    color: var(--gray-600);
    font-style: italic;
}

.reading-image {
    margin-bottom: var(--spacing-lg);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.reading-image img {
    width: 100%;
    height: auto;
}

.reading-content {
    margin-bottom: var(--spacing-lg);
}

.reading-excerpt {
    font-size: var(--text-lg);
    font-weight: 500;
    color: var(--gray-700);
    line-height: 1.6;
    margin-bottom: var(--spacing-lg);
    padding-left: var(--spacing-md);
    border-left: 4px solid var(--primary-500);
}

.reading-body {
    font-size: var(--text-base);
    line-height: 1.7;
    color: var(--gray-800);
}

.reading-footer {
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--gray-200);
}

.reading-actions {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.reading-action-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--gray-100);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    font-size: var(--text-sm);
}

.reading-action-btn:hover {
    background: var(--primary-100);
    border-color: var(--primary-500);
    color: var(--primary-700);
}

.related-stocks-section h4 {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
    margin-bottom: var(--spacing-sm);
}

.related-stocks-list {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.related-stock-link {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-sm);
    text-decoration: none;
    font-size: var(--text-sm);
    font-weight: 600;
    transition: all var(--transition-fast) var(--easing-standard);
}

.related-stock-link:hover {
    background: var(--primary-500);
    color: white;
    text-decoration: none;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .news-layout {
        grid-template-columns: 1fr;
    }
    
    .news-filters,
    .news-reading-pane {
        position: static;
        max-height: none;
    }
    
    .news-reading-pane {
        order: -1;
    }
}

@media (max-width: 640px) {
    .news-feed.view-list .news-article {
        flex-direction: column;
    }
    
    .news-feed.view-list .article-image {
        width: 100%;
    }
    
    .feed-controls {
        flex-direction: column;
        gap: var(--spacing-sm);
        align-items: flex-start;
    }
    
    .article-meta {
        flex-wrap: wrap;
    }
    
    .related-stocks {
        margin-left: 0;
        margin-top: var(--spacing-xs);
    }
}

/* Dark Mode Adjustments */
[data-theme="dark"] .filter-group-title,
[data-theme="dark"] .reading-author {
    color: var(--gray-300);
}

[data-theme="dark"] .checkmark {
    border-color: var(--gray-600);
}

[data-theme="dark"] .reading-pane-header,
[data-theme="dark"] .chart-legend {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .reading-pane-placeholder {
    color: var(--gray-500);
}

[data-theme="dark"] .reading-header,
[data-theme="dark"] .reading-footer {
    border-color: var(--gray-700);
}

[data-theme="dark"] .reading-body {
    color: var(--gray-200);
}

[data-theme="dark"] .reading-excerpt {
    color: var(--gray-300);
}
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>