<?php
/**
 * Template Name: Personalized News
 * Description: Intelligent news curation based on user holdings and interests
 */

// Security check - require user authentication
if (!is_user_logged_in()) {
    wp_redirect(home_url('/signup/?redirect_to=' . urlencode($_SERVER['REQUEST_URI'])));
    exit;
}

get_header(); ?>

<div class="personalized-news-container">
    <div class="container-fluid">
        <div class="row">
            <!-- Page Header -->
            <div class="col-12">
                <div class="page-header">
                    <h1 class="page-title">
                        <i class="fas fa-newspaper"></i> Personalized News Feed
                    </h1>
                    <p class="page-description">
                        Get news tailored to your stock holdings and interests with intelligent curation
                    </p>
                </div>
            </div>
        </div>

        <!-- News Controls -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="news-controls-bar">
                    <div class="news-actions">
                        <button class="btn btn-primary" id="refresh-news-btn">
                            <i class="fas fa-sync-alt"></i> Refresh News
                        </button>
                        <button class="btn btn-success" id="sync-portfolio-btn">
                            <i class="fas fa-sync"></i> Sync with Portfolio
                        </button>
                        <button class="btn btn-info" id="news-preferences-btn">
                            <i class="fas fa-cog"></i> Preferences
                        </button>
                        <button class="btn btn-warning" id="news-analytics-btn">
                            <i class="fas fa-chart-bar"></i> Analytics
                        </button>
                    </div>
                    <div class="news-filters">
                        <select id="news-category" class="form-select">
                            <option value="">All Categories</option>
                            <option value="earnings">Earnings</option>
                            <option value="merger">Mergers & Acquisitions</option>
                            <option value="analyst">Analyst Reports</option>
                            <option value="general">General News</option>
                            <option value="market">Market News</option>
                            <option value="regulatory">Regulatory</option>
                            <option value="insider">Insider Trading</option>
                        </select>
                        <select id="news-sort" class="form-select">
                            <option value="relevance">Sort by Relevance</option>
                            <option value="date">Sort by Date</option>
                            <option value="popularity">Sort by Popularity</option>
                        </select>
                        <select id="news-timeframe" class="form-select">
                            <option value="24h">Last 24 Hours</option>
                            <option value="3d">Last 3 Days</option>
                            <option value="1w">Last Week</option>
                            <option value="1m">Last Month</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- News Feed Tabs -->
        <div class="row">
            <div class="col-12">
                <ul class="nav nav-tabs" id="news-tabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="for-you-tab" data-bs-toggle="tab" 
                                data-bs-target="#for-you" type="button" role="tab">
                            <i class="fas fa-user"></i> For You
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="portfolio-news-tab" data-bs-toggle="tab" 
                                data-bs-target="#portfolio-news" type="button" role="tab">
                            <i class="fas fa-briefcase"></i> Portfolio News
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="watchlist-news-tab" data-bs-toggle="tab" 
                                data-bs-target="#watchlist-news" type="button" role="tab">
                            <i class="fas fa-eye"></i> Watchlist News
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="trending-news-tab" data-bs-toggle="tab" 
                                data-bs-target="#trending-news" type="button" role="tab">
                            <i class="fas fa-fire"></i> Trending
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="read-later-tab" data-bs-toggle="tab" 
                                data-bs-target="#read-later" type="button" role="tab">
                            <i class="fas fa-bookmark"></i> Read Later <span class="badge bg-secondary" id="read-later-count">0</span>
                        </button>
                    </li>
                </ul>
            </div>
        </div>

        <!-- News Content -->
        <div class="tab-content" id="news-tab-content">
            <!-- For You Tab -->
            <div class="tab-pane fade show active" id="for-you" role="tabpanel">
                <div class="news-feed" id="for-you-feed">
                    <!-- Personalized news will be loaded here -->
                    <div class="loading-spinner text-center">
                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                        <p>Loading your personalized news feed...</p>
                    </div>
                </div>
            </div>

            <!-- Portfolio News Tab -->
            <div class="tab-pane fade" id="portfolio-news" role="tabpanel">
                <div class="news-feed" id="portfolio-news-feed">
                    <!-- Portfolio-related news will be loaded here -->
                </div>
            </div>

            <!-- Watchlist News Tab -->
            <div class="tab-pane fade" id="watchlist-news" role="tabpanel">
                <div class="news-feed" id="watchlist-news-feed">
                    <!-- Watchlist-related news will be loaded here -->
                </div>
            </div>

            <!-- Trending News Tab -->
            <div class="tab-pane fade" id="trending-news" role="tabpanel">
                <div class="news-feed" id="trending-news-feed">
                    <!-- Trending news will be loaded here -->
                </div>
            </div>

            <!-- Read Later Tab -->
            <div class="tab-pane fade" id="read-later" role="tabpanel">
                <div class="news-feed" id="read-later-feed">
                    <!-- Saved articles will be loaded here -->
                </div>
            </div>
        </div>

        <!-- Load More -->
        <div class="row mt-4">
            <div class="col-12 text-center">
                <button class="btn btn-outline-primary" id="load-more-news">
                    <i class="fas fa-plus"></i> Load More News
                </button>
            </div>
        </div>
    </div>
</div>

<!-- News Preferences Modal -->
<div class="modal fade" id="newsPreferencesModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">News Preferences</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="news-preferences-form">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Followed Stocks</h6>
                            <div class="mb-3">
                                <label for="followed-stocks" class="form-label">Additional Stocks to Follow</label>
                                <textarea class="form-control" id="followed-stocks" rows="4" 
                                          placeholder="Enter stock tickers separated by commas&#10;Example: AAPL, MSFT, GOOGL"></textarea>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Preferred Categories</h6>
                            <div class="preferred-categories">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-earnings" value="earnings">
                                    <label class="form-check-label" for="pref-earnings">Earnings Reports</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-merger" value="merger">
                                    <label class="form-check-label" for="pref-merger">Mergers & Acquisitions</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-analyst" value="analyst">
                                    <label class="form-check-label" for="pref-analyst">Analyst Reports</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-general" value="general">
                                    <label class="form-check-label" for="pref-general">General News</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-market" value="market">
                                    <label class="form-check-label" for="pref-market">Market News</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-regulatory" value="regulatory">
                                    <label class="form-check-label" for="pref-regulatory">Regulatory Updates</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pref-insider" value="insider">
                                    <label class="form-check-label" for="pref-insider">Insider Trading</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <hr>
                    <div class="row">
                        <div class="col-md-6">
                            <h6>News Frequency</h6>
                            <div class="mb-3">
                                <label for="news-frequency" class="form-label">How often would you like news updates?</label>
                                <select class="form-select" id="news-frequency">
                                    <option value="realtime">Real-time</option>
                                    <option value="hourly">Hourly</option>
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Followed Sectors</h6>
                            <div class="mb-3">
                                <label for="followed-sectors" class="form-label">Industries to Follow</label>
                                <textarea class="form-control" id="followed-sectors" rows="3" 
                                          placeholder="Enter sectors separated by commas&#10;Example: Technology, Healthcare, Energy"></textarea>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <h6>Smart Filtering</h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="auto-sync-portfolio">
                                <label class="form-check-label" for="auto-sync-portfolio">
                                    Automatically sync with portfolio changes
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="exclude-low-relevance">
                                <label class="form-check-label" for="exclude-low-relevance">
                                    Hide low relevance articles (score below 3.0)
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="prioritize-holdings">
                                <label class="form-check-label" for="prioritize-holdings">
                                    Prioritize news for stocks you own
                                </label>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-preferences-btn">Save Preferences</button>
            </div>
        </div>
    </div>
</div>

<!-- News Analytics Modal -->
<div class="modal fade" id="newsAnalyticsModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">News Consumption Analytics</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="news-analytics-content">
                    <!-- Analytics content will be loaded here -->
                </div>
            </div>
        </div>
    </div>
</div>

<!-- News Article Detail Modal -->
<div class="modal fade" id="newsArticleModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="article-title">Article Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="article-content">
                    <!-- Article content will be loaded here -->
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-outline-primary" id="save-article-btn">
                    <i class="fas fa-bookmark"></i> Save for Later
                </button>
                <button type="button" class="btn btn-primary" id="open-article-btn" target="_blank">
                    <i class="fas fa-external-link-alt"></i> Read Full Article
                </button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize Personalized News functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize News Manager
    const newsManager = new NewsManager();
    newsManager.init();
    
    // Load personalized news feed
    newsManager.loadPersonalizedFeed();
    
    // Set up event listeners
    document.getElementById('refresh-news-btn').addEventListener('click', function() {
        newsManager.refreshNews();
    });
    
    document.getElementById('sync-portfolio-btn').addEventListener('click', function() {
        newsManager.syncPortfolioStocks();
    });
    
    document.getElementById('news-preferences-btn').addEventListener('click', function() {
        newsManager.loadPreferences();
        const modal = new bootstrap.Modal(document.getElementById('newsPreferencesModal'));
        modal.show();
    });
    
    document.getElementById('news-analytics-btn').addEventListener('click', function() {
        newsManager.loadAnalytics();
        const modal = new bootstrap.Modal(document.getElementById('newsAnalyticsModal'));
        modal.show();
    });
    
    // Filter and sorting
    document.getElementById('news-category').addEventListener('change', function() {
        newsManager.filterByCategory(this.value);
    });
    
    document.getElementById('news-sort').addEventListener('change', function() {
        newsManager.sortNews(this.value);
    });
    
    document.getElementById('news-timeframe').addEventListener('change', function() {
        newsManager.filterByTimeframe(this.value);
    });
    
    // Tab switching
    document.querySelectorAll('#news-tabs button[data-bs-toggle="tab"]').forEach(function(tab) {
        tab.addEventListener('shown.bs.tab', function(e) {
            const targetTab = e.target.getAttribute('data-bs-target');
            newsManager.loadTabContent(targetTab);
        });
    });
    
    // Form submissions
    document.getElementById('save-preferences-btn').addEventListener('click', function() {
        newsManager.savePreferences();
    });
    
    // Load more news
    document.getElementById('load-more-news').addEventListener('click', function() {
        newsManager.loadMoreNews();
    });
    
    // Article interactions
    document.getElementById('save-article-btn').addEventListener('click', function() {
        newsManager.saveArticleForLater();
    });
    
    document.getElementById('open-article-btn').addEventListener('click', function() {
        newsManager.openFullArticle();
    });
    
    // Auto-refresh news feed
    setInterval(function() {
        newsManager.autoRefreshNews();
    }, 300000); // Refresh every 5 minutes
    
    // Track reading behavior for analytics
    document.addEventListener('scroll', function() {
        newsManager.trackScrollBehavior();
    });
    
    // Save tab preferences
    document.addEventListener('shown.bs.tab', function(e) {
        localStorage.setItem('activeNewsTab', e.target.id);
    });
    
    // Load saved tab preference
    const savedTab = localStorage.getItem('activeNewsTab');
    if (savedTab) {
        const tabElement = document.getElementById(savedTab);
        if (tabElement) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
        }
    }
});

// Handle news article clicks globally
document.addEventListener('click', function(e) {
    if (e.target.closest('.news-item')) {
        const newsItem = e.target.closest('.news-item');
        const newsId = newsItem.dataset.newsId;
        
        if (e.target.closest('.bookmark-btn')) {
            // Handle bookmark click
            e.preventDefault();
            newsManager.toggleBookmark(newsId);
        } else if (e.target.closest('.share-btn')) {
            // Handle share click
            e.preventDefault();
            newsManager.shareArticle(newsId);
        } else {
            // Handle article click
            newsManager.markAsRead(newsId);
            newsManager.markAsClicked(newsId);
        }
    }
});
</script>

<?php get_footer(); ?>