<?php
/**
 * News Item Component
 * Reusable component for displaying personalized news articles
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Set default values
$article = $args['article'] ?? null;
$show_actions = $args['show_actions'] ?? true;
$layout = $args['layout'] ?? 'default'; // default, compact, detailed
$show_content = $args['show_content'] ?? true;

if (!$article) {
    return;
}

// Format date
$published_date = date('M j, Y g:i A', strtotime($article['published_at']));
$time_ago = human_time_diff(strtotime($article['published_at']), current_time('timestamp')) . ' ago';

// Relevance score color
$relevance_class = '';
if ($article['relevance_score'] >= 8) {
    $relevance_class = 'high';
} elseif ($article['relevance_score'] >= 6) {
    $relevance_class = 'medium';
} else {
    $relevance_class = 'low';
}

?>

<article class="news-item layout-<?php echo esc_attr($layout); ?> relevance-<?php echo esc_attr($relevance_class); ?>" 
         data-news-id="<?php echo esc_attr($article['id']); ?>"
         data-category="<?php echo esc_attr($article['category']); ?>"
         data-relevance="<?php echo esc_attr($article['relevance_score']); ?>">
         
    <!-- News Header -->
    <div class="news-header">
        <div class="news-meta-top">
            <div class="news-source-info">
                <span class="news-source"><?php echo esc_html($article['source']); ?></span>
                <span class="news-date" title="<?php echo esc_attr($published_date); ?>">
                    <?php echo esc_html($time_ago); ?>
                </span>
            </div>
            
            <div class="news-indicators">
                <span class="relevance-score relevance-<?php echo $relevance_class; ?>" 
                      title="Relevance Score: <?php echo number_format($article['relevance_score'], 1); ?>/10">
                    <?php echo number_format($article['relevance_score'], 1); ?>
                </span>
                
                <span class="news-category">
                    <span class="badge bg-secondary"><?php echo esc_html(ucfirst($article['category'])); ?></span>
                </span>
            </div>
        </div>
        
        <h5 class="news-title">
            <a href="<?php echo esc_url($article['url']); ?>" 
               target="_blank" 
               rel="noopener noreferrer"
               onclick="newsManager.markAsClicked(<?php echo $article['id']; ?>)">
                <?php echo esc_html($article['title']); ?>
            </a>
        </h5>
    </div>
    
    <!-- News Content -->
    <?php if ($show_content && $layout !== 'compact'): ?>
        <div class="news-content">
            <?php if (!empty($article['summary'])): ?>
                <p class="news-summary">
                    <?php echo esc_html($article['summary']); ?>
                </p>
            <?php elseif (!empty($article['content'])): ?>
                <p class="news-summary">
                    <?php echo esc_html(wp_trim_words($article['content'], 50, '...')); ?>
                </p>
            <?php endif; ?>
            
            <!-- Related Stocks -->
            <?php if (!empty($article['related_stocks']) && is_array($article['related_stocks'])): ?>
                <div class="related-stocks">
                    <strong class="related-label">Related Stocks:</strong>
                    <div class="stock-tickers">
                        <?php foreach ($article['related_stocks'] as $ticker): ?>
                            <span class="stock-ticker" onclick="window.open('/stock-detail/<?php echo strtolower($ticker); ?>/', '_blank')">
                                <?php echo esc_html($ticker); ?>
                            </span>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>
    
    <!-- News Footer -->
    <div class="news-footer">
        <div class="news-engagement">
            <?php if (!empty($article['read_count'])): ?>
                <span class="read-count">
                    <i class="fas fa-eye"></i>
                    <?php echo number_format($article['read_count']); ?> reads
                </span>
            <?php endif; ?>
            
            <?php if (!empty($article['click_count'])): ?>
                <span class="click-count">
                    <i class="fas fa-mouse-pointer"></i>
                    <?php echo number_format($article['click_count']); ?> clicks
                </span>
            <?php endif; ?>
        </div>
        
        <?php if ($show_actions): ?>
            <div class="news-actions">
                <button class="btn btn-sm btn-outline-primary bookmark-btn" 
                        onclick="newsManager.toggleBookmark(<?php echo $article['id']; ?>)"
                        title="Save for later">
                    <i class="fas fa-bookmark"></i>
                    <span class="btn-text">Save</span>
                </button>
                
                <button class="btn btn-sm btn-outline-secondary share-btn" 
                        onclick="newsManager.shareArticle(<?php echo $article['id']; ?>)"
                        title="Share article">
                    <i class="fas fa-share"></i>
                    <span class="btn-text">Share</span>
                </button>
                
                <button class="btn btn-sm btn-outline-info" 
                        onclick="newsManager.markAsRead(<?php echo $article['id']; ?>); window.open('<?php echo esc_js($article['url']); ?>', '_blank')"
                        title="Read full article">
                    <i class="fas fa-external-link-alt"></i>
                    <span class="btn-text">Read</span>
                </button>
                
                <?php if ($layout === 'detailed'): ?>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                type="button" 
                                data-bs-toggle="dropdown" 
                                aria-expanded="false">
                            <i class="fas fa-ellipsis-h"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <a class="dropdown-item" href="#" onclick="newsManager.reportArticle(<?php echo $article['id']; ?>)">
                                    <i class="fas fa-flag"></i> Report Article
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="#" onclick="newsManager.hideSource('<?php echo esc_js($article['source']); ?>')">
                                    <i class="fas fa-eye-slash"></i> Hide Source
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="#" onclick="newsManager.hideCategory('<?php echo esc_js($article['category']); ?>')">
                                    <i class="fas fa-times"></i> Hide Category
                                </a>
                            </li>
                        </ul>
                    </div>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Reading Progress (for detailed layout) -->
    <?php if ($layout === 'detailed'): ?>
        <div class="reading-progress">
            <div class="progress-bar" data-article-id="<?php echo $article['id']; ?>"></div>
        </div>
    <?php endif; ?>
</article>

.news-item {
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
    margin-bottom: var(--spacing-lg, 1.5rem);
    transition: all var(--transition-normal, 0.3s ease-in-out);
    box-shadow: var(--shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
    position: relative;
}

.news-item:hover {
    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
    border-color: var(--primary-color, #2563eb);
}

.news-item.layout-compact {
    padding: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-md, 1rem);
}

.news-item.layout-detailed {
    padding: var(--spacing-xl, 2rem);
}

/* Relevance indicators */
.news-item.relevance-high {
    border-left: 4px solid var(--success-color, #059669);
}

.news-item.relevance-medium {
    border-left: 4px solid var(--warning-color, #d97706);
}

.news-item.relevance-low {
    border-left: 4px solid var(--secondary-color, #64748b);
}

/* Header */
.news-header {
    margin-bottom: var(--spacing-md, 1rem);
}

.news-meta-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm, 0.5rem);
    flex-wrap: wrap;
    gap: var(--spacing-sm, 0.5rem);
}

.news-source-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
    flex-wrap: wrap;
}

.news-source {
    font-weight: 600;
    color: var(--primary-color, #2563eb);
    font-size: 0.875rem;
}

.news-date {
    color: var(--text-secondary, #64748b);
    font-size: 0.75rem;
}

.news-indicators {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
}

.relevance-score {
    background: var(--bg-muted, #f1f5f9);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary, #64748b);
}

.relevance-score.relevance-high {
    background: rgba(5, 150, 105, 0.1);
    color: var(--success-color, #059669);
}

.relevance-score.relevance-medium {
    background: rgba(217, 119, 6, 0.1);
    color: var(--warning-color, #d97706);
}

.relevance-score.relevance-low {
    background: var(--bg-muted, #f1f5f9);
    color: var(--text-secondary, #64748b);
}

.news-category .badge {
    font-size: 0.65rem;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}

.news-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    line-height: 1.4;
}

.news-title a {
    color: var(--text-primary, #1e293b);
    text-decoration: none;
    transition: color var(--transition-fast, 0.15s ease-in-out);
}

.news-title a:hover {
    color: var(--primary-color, #2563eb);
    text-decoration: none;
}

.layout-compact .news-title {
    font-size: 1rem;
}

.layout-detailed .news-title {
    font-size: 1.375rem;
}

/* Content */
.news-content {
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.news-summary {
    color: var(--text-primary, #1e293b);
    line-height: 1.6;
    margin: 0 0 var(--spacing-md, 1rem) 0;
}

.related-stocks {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
    flex-wrap: wrap;
    font-size: 0.875rem;
}

.related-label {
    color: var(--text-secondary, #64748b);
    white-space: nowrap;
}

.stock-tickers {
    display: flex;
    gap: var(--spacing-xs, 0.25rem);
    flex-wrap: wrap;
}

.stock-ticker {
    background: var(--primary-color, #2563eb);
    color: white;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all var(--transition-fast, 0.15s ease-in-out);
}

.stock-ticker:hover {
    background: var(--primary-hover, #1d4ed8);
    transform: translateY(-1px);
}

/* Footer */
.news-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--spacing-md, 1rem);
    border-top: 1px solid var(--border-muted, #f1f5f9);
    flex-wrap: wrap;
    gap: var(--spacing-sm, 0.5rem);
}

.news-engagement {
    display: flex;
    gap: var(--spacing-md, 1rem);
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
}

.news-engagement span {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
}

.news-actions {
    display: flex;
    gap: var(--spacing-sm, 0.5rem);
    align-items: center;
}

.news-actions .btn {
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
}

.news-actions .btn-text {
    display: none;
}

.layout-detailed .news-actions .btn-text {
    display: inline;
}

.bookmark-btn.saved {
    background: var(--warning-color, #d97706);
    border-color: var(--warning-color, #d97706);
    color: white;
}

/* Reading progress */
.reading-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--bg-muted, #f1f5f9);
    border-radius: 0 0 var(--radius-lg, 0.5rem) var(--radius-lg, 0.5rem);
}

.progress-bar {
    height: 100%;
    background: var(--primary-color, #2563eb);
    width: 0%;
    transition: width 0.3s ease;
    border-radius: 0 0 var(--radius-lg, 0.5rem) var(--radius-lg, 0.5rem);
}

/* Responsive Design */
@media (max-width: 768px) {
    .news-meta-top {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .news-title {
        font-size: 1rem;
    }
    
    .layout-detailed .news-title {
        font-size: 1.125rem;
    }
    
    .news-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md, 1rem);
    }
    
    .news-actions {
        width: 100%;
        justify-content: space-between;
    }
    
    .news-actions .btn {
        flex: 1;
        justify-content: center;
    }
    
    .news-actions .btn-text {
        display: inline;
    }
    
    .related-stocks {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media (max-width: 480px) {
    .news-item {
        padding: var(--spacing-md, 1rem);
    }
    
    .layout-detailed {
        padding: var(--spacing-lg, 1.5rem);
    }
    
    .news-actions {
        flex-direction: column;
        gap: var(--spacing-xs, 0.25rem);
    }
    
    .news-actions .btn {
        width: 100%;
    }
}

/* Animation for new articles */
@keyframes slideInFromTop {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.news-item.new-article {
    animation: slideInFromTop 0.5s ease-out;
}

<script>
// Track reading progress for detailed articles
document.addEventListener('DOMContentLoaded', function() {
    if ('<?php echo $layout; ?>' === 'detailed') {
        const article = document.querySelector('[data-news-id="<?php echo $article['id']; ?>"]');
        const progressBar = article?.querySelector('.progress-bar');
        
        if (article && progressBar) {
            let hasStartedReading = false;
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !hasStartedReading) {
                        hasStartedReading = true;
                        // Mark as viewed
                        if (typeof newsManager !== 'undefined') {
                            newsManager.markAsRead(<?php echo $article['id']; ?>);
                        }
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(article);
            
            // Simulate reading progress based on scroll
            let readingStartTime = null;
            window.addEventListener('scroll', () => {
                if (!readingStartTime && hasStartedReading) {
                    readingStartTime = Date.now();
                }
                
                if (readingStartTime) {
                    const elapsed = (Date.now() - readingStartTime) / 1000; // seconds
                    const progress = Math.min((elapsed / 30) * 100, 100); // 30 seconds = 100%
                    progressBar.style.width = progress + '%';
                }
            });
        }
    }
});
</script>