<?php
/**
 * The template for displaying search results pages
 *
 * @package RetailTradeScanner
 */

get_header();

$search_query = get_search_query();
$search_results = new WP_Query(array(
    's' => $search_query,
    'posts_per_page' => 10
));

// Mock stock search results for demonstration
$stock_results = array();
if ($search_query) {
    $mock_stocks = array(
        'AAPL' => array('name' => 'Apple Inc.', 'price' => '$182.34', 'change' => '+2.45%'),
        'TSLA' => array('name' => 'Tesla Inc.', 'price' => '$245.67', 'change' => '-1.28%'),
        'NVDA' => array('name' => 'NVIDIA Corporation', 'price' => '$456.78', 'change' => '+3.67%'),
        'MSFT' => array('name' => 'Microsoft Corporation', 'price' => '$412.89', 'change' => '+1.23%'),
        'GOOGL' => array('name' => 'Alphabet Inc.', 'price' => '$142.56', 'change' => '+0.89%')
    );
    
    foreach ($mock_stocks as $symbol => $data) {
        if (stripos($symbol, $search_query) !== false || stripos($data['name'], $search_query) !== false) {
            $stock_results[] = array_merge(['symbol' => $symbol], $data);
        }
    }
}
?>

<div class="search-page">
    <div class="container">
        <!-- Search Header -->
        <div class="search-header">
            <div class="search-info">
                <h1 class="search-title">
                    <?php
                    printf(
                        esc_html__('Search Results for "%s"', 'retail-trade-scanner'),
                        '<span class="search-term">' . esc_html($search_query) . '</span>'
                    );
                    ?>
                </h1>
                <p class="search-meta">
                    <?php
                    $total_results = count($stock_results) + $search_results->found_posts;
                    printf(
                        esc_html(_n('%d result found', '%d results found', $total_results, 'retail-trade-scanner')),
                        $total_results
                    );
                    ?>
                </p>
            </div>
            
            <!-- Search Form -->
            <div class="search-form-container">
                <form class="search-form" role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
                    <div class="search-input-group">
                        <input type="search" 
                               name="s" 
                               class="search-input" 
                               placeholder="<?php esc_attr_e('Search stocks, content, or features...', 'retail-trade-scanner'); ?>"
                               value="<?php echo esc_attr($search_query); ?>"
                               aria-label="<?php esc_attr_e('Search', 'retail-trade-scanner'); ?>">
                        <button type="submit" class="search-button">
                            <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <?php if ($search_query) : ?>
            <div class="search-results">
                
                <!-- Stock Results -->
                <?php if (!empty($stock_results)) : ?>
                    <section class="results-section stock-results">
                        <div class="section-header">
                            <h2 class="section-title">
                                <?php echo rts_get_icon('trending-up', ['width' => '24', 'height' => '24']); ?>
                                <?php esc_html_e('Stock Matches', 'retail-trade-scanner'); ?>
                                <span class="result-count"><?php echo count($stock_results); ?></span>
                            </h2>
                        </div>
                        
                        <div class="stock-results-grid">
                            <?php foreach ($stock_results as $stock) : ?>
                                <div class="stock-result-card glass-card">
                                    <div class="stock-symbol"><?php echo esc_html($stock['symbol']); ?></div>
                                    <div class="stock-name"><?php echo esc_html($stock['name']); ?></div>
                                    <div class="stock-price">
                                        <span class="price"><?php echo esc_html($stock['price']); ?></span>
                                        <span class="change <?php echo strpos($stock['change'], '+') === 0 ? 'positive' : 'negative'; ?>">
                                            <?php echo esc_html($stock['change']); ?>
                                        </span>
                                    </div>
                                    <div class="stock-actions">
                                        <button class="btn btn-sm btn-outline">
                                            <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                                            <?php esc_html_e('Add to Watchlist', 'retail-trade-scanner'); ?>
                                        </button>
                                        <button class="btn btn-sm btn-primary">
                                            <?php echo rts_get_icon('bar-chart', ['width' => '16', 'height' => '16']); ?>
                                            <?php esc_html_e('View Chart', 'retail-trade-scanner'); ?>
                                        </button>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </section>
                <?php endif; ?>
                
                <!-- Content Results -->
                <?php if ($search_results->have_posts()) : ?>
                    <section class="results-section content-results">
                        <div class="section-header">
                            <h2 class="section-title">
                                <?php echo rts_get_icon('file-text', ['width' => '24', 'height' => '24']); ?>
                                <?php esc_html_e('Content Matches', 'retail-trade-scanner'); ?>
                                <span class="result-count"><?php echo $search_results->found_posts; ?></span>
                            </h2>
                        </div>
                        
                        <div class="content-results-list">
                            <?php while ($search_results->have_posts()) : $search_results->the_post(); ?>
                                <article class="content-result-card">
                                    <div class="result-header">
                                        <h3 class="result-title">
                                            <a href="<?php the_permalink(); ?>" class="result-link">
                                                <?php the_title(); ?>
                                            </a>
                                        </h3>
                                        <div class="result-meta">
                                            <span class="post-type">
                                                <?php echo esc_html(get_post_type_object(get_post_type())->labels->singular_name); ?>
                                            </span>
                                            <span class="meta-separator">•</span>
                                            <time datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                                                <?php echo esc_html(get_the_date()); ?>
                                            </time>
                                        </div>
                                    </div>
                                    
                                    <div class="result-content">
                                        <p class="result-excerpt">
                                            <?php
                                            $excerpt = get_the_excerpt();
                                            if ($excerpt) {
                                                echo wp_kses_post(wp_trim_words($excerpt, 30));
                                            } else {
                                                echo wp_kses_post(wp_trim_words(get_the_content(), 30));
                                            }
                                            ?>
                                        </p>
                                    </div>
                                    
                                    <div class="result-actions">
                                        <a href="<?php the_permalink(); ?>" class="result-action-link">
                                            <?php esc_html_e('Read More', 'retail-trade-scanner'); ?>
                                            <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                                        </a>
                                    </div>
                                </article>
                            <?php endwhile; ?>
                        </div>
                        
                        <!-- Pagination -->
                        <?php if ($search_results->max_num_pages > 1) : ?>
                            <div class="search-pagination">
                                <?php
                                echo paginate_links(array(
                                    'total' => $search_results->max_num_pages,
                                    'current' => max(1, get_query_var('paged')),
                                    'format' => '?paged=%#%',
                                    'show_all' => false,
                                    'end_size' => 1,
                                    'mid_size' => 2,
                                    'prev_next' => true,
                                    'prev_text' => rts_get_icon('chevron-left', ['width' => '16', 'height' => '16']) . ' ' . __('Previous', 'retail-trade-scanner'),
                                    'next_text' => __('Next', 'retail-trade-scanner') . ' ' . rts_get_icon('chevron-right', ['width' => '16', 'height' => '16']),
                                    'add_args' => array('s' => $search_query)
                                ));
                                ?>
                            </div>
                        <?php endif; ?>
                    </section>
                <?php endif; ?>
                
                <!-- No Results -->
                <?php if (empty($stock_results) && !$search_results->have_posts()) : ?>
                    <div class="no-results">
                        <div class="no-results-icon">
                            <?php echo rts_get_icon('search', ['width' => '80', 'height' => '80']); ?>
                        </div>
                        <h2 class="no-results-title"><?php esc_html_e('No results found', 'retail-trade-scanner'); ?></h2>
                        <p class="no-results-text">
                            <?php
                            printf(
                                esc_html__('We couldn\'t find any results for "%s". Try adjusting your search terms or browse our popular content below.', 'retail-trade-scanner'),
                                esc_html($search_query)
                            );
                            ?>
                        </p>
                        
                        <!-- Search Suggestions -->
                        <div class="search-suggestions">
                            <h3><?php esc_html_e('Search suggestions:', 'retail-trade-scanner'); ?></h3>
                            <ul class="suggestions-list">
                                <li><?php esc_html_e('Check your spelling', 'retail-trade-scanner'); ?></li>
                                <li><?php esc_html_e('Try more general keywords', 'retail-trade-scanner'); ?></li>
                                <li><?php esc_html_e('Use fewer keywords', 'retail-trade-scanner'); ?></li>
                                <li><?php esc_html_e('Try stock symbols (e.g., AAPL, TSLA)', 'retail-trade-scanner'); ?></li>
                            </ul>
                        </div>
                        
                        <!-- Popular Searches -->
                        <div class="popular-searches">
                            <h3><?php esc_html_e('Popular searches:', 'retail-trade-scanner'); ?></h3>
                            <div class="popular-tags">
                                <a href="?s=AAPL" class="popular-tag">AAPL</a>
                                <a href="?s=TSLA" class="popular-tag">TSLA</a>
                                <a href="?s=portfolio" class="popular-tag">Portfolio</a>
                                <a href="?s=alerts" class="popular-tag">Alerts</a>
                                <a href="?s=scanner" class="popular-tag">Scanner</a>
                                <a href="?s=news" class="popular-tag">News</a>
                            </div>
                        </div>
                    </div>
                <?php endif; ?>
                
            </div>
        <?php else : ?>
            <!-- Empty Search State -->
            <div class="empty-search">
                <div class="empty-search-content">
                    <div class="empty-search-icon">
                        <?php echo rts_get_icon('search', ['width' => '80', 'height' => '80']); ?>
                    </div>
                    <h2 class="empty-search-title"><?php esc_html_e('What are you looking for?', 'retail-trade-scanner'); ?></h2>
                    <p class="empty-search-text">
                        <?php esc_html_e('Search for stocks, market data, platform features, or help content.', 'retail-trade-scanner'); ?>
                    </p>
                    
                    <!-- Quick Search Categories -->
                    <div class="quick-search-categories">
                        <h3><?php esc_html_e('Quick search categories:', 'retail-trade-scanner'); ?></h3>
                        <div class="category-grid">
                            <a href="?s=stocks" class="category-card">
                                <?php echo rts_get_icon('trending-up', ['width' => '24', 'height' => '24']); ?>
                                <span><?php esc_html_e('Stocks', 'retail-trade-scanner'); ?></span>
                            </a>
                            <a href="?s=portfolio" class="category-card">
                                <?php echo rts_get_icon('portfolio', ['width' => '24', 'height' => '24']); ?>
                                <span><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></span>
                            </a>
                            <a href="?s=alerts" class="category-card">
                                <?php echo rts_get_icon('bell', ['width' => '24', 'height' => '24']); ?>
                                <span><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></span>
                            </a>
                            <a href="?s=help" class="category-card">
                                <?php echo rts_get_icon('help-circle', ['width' => '24', 'height' => '24']); ?>
                                <span><?php esc_html_e('Help', 'retail-trade-scanner'); ?></span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        <?php endif; ?>
        
    </div>
</div>

<?php wp_reset_postdata(); ?>

<style>
/* Search Page Styles */
.search-page {
    min-height: 80vh;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    padding: var(--spacing-2xl) 0;
}

.search-header {
    margin-bottom: var(--spacing-2xl);
    text-align: center;
}

.search-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-sm);
}

.search-term {
    color: var(--primary-600);
}

.search-meta {
    color: var(--gray-600);
    margin: 0 0 var(--spacing-xl);
}

.search-form-container {
    max-width: 600px;
    margin: 0 auto;
}

.search-input-group {
    display: flex;
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}

.search-input {
    flex: 1;
    padding: var(--spacing-lg);
    border: 2px solid var(--primary-200);
    border-right: none;
    font-size: var(--text-lg);
    outline: none;
    background: var(--surface);
}

.search-input:focus {
    border-color: var(--primary-500);
}

.search-button {
    padding: var(--spacing-lg);
    background: var(--primary-500);
    color: white;
    border: 2px solid var(--primary-500);
    cursor: pointer;
    transition: background-color var(--transition-fast) var(--easing-standard);
    min-width: 60px;
}

.search-button:hover {
    background: var(--primary-600);
    border-color: var(--primary-600);
}

/* Results Sections */
.results-section {
    margin-bottom: var(--spacing-2xl);
}

.section-header {
    margin-bottom: var(--spacing-xl);
}

.section-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0;
}

.result-count {
    font-size: var(--text-base);
    color: var(--gray-600);
    font-weight: 500;
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--gray-100);
    border-radius: var(--radius-full);
}

/* Stock Results */
.stock-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.stock-result-card {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    transition: all var(--transition-normal) var(--easing-standard);
}

.stock-result-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.stock-symbol {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
}

.stock-name {
    color: var(--gray-600);
    margin-bottom: var(--spacing-sm);
}

.stock-price {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.price {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
}

.change {
    font-size: var(--text-sm);
    font-weight: 600;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
}

.change.positive {
    background: var(--success-light);
    color: var(--success-dark);
}

.change.negative {
    background: var(--danger-light);
    color: var(--danger-dark);
}

.stock-actions {
    display: flex;
    gap: var(--spacing-sm);
}

/* Content Results */
.content-results-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.content-result-card {
    background: var(--surface);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    transition: all var(--transition-fast) var(--easing-standard);
}

.content-result-card:hover {
    border-color: var(--primary-300);
    box-shadow: var(--shadow-md);
}

.result-header {
    margin-bottom: var(--spacing-md);
}

.result-title {
    margin: 0 0 var(--spacing-sm);
}

.result-link {
    color: var(--gray-900);
    text-decoration: none;
    font-size: var(--text-lg);
    font-weight: 600;
    transition: color var(--transition-fast) var(--easing-standard);
}

.result-link:hover {
    color: var(--primary-600);
    text-decoration: none;
}

.result-meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
    color: var(--gray-500);
}

.post-type {
    font-weight: 600;
    color: var(--primary-600);
}

.meta-separator {
    color: var(--gray-300);
}

.result-content {
    margin-bottom: var(--spacing-lg);
}

.result-excerpt {
    color: var(--gray-700);
    line-height: 1.6;
    margin: 0;
}

.result-actions {
    display: flex;
    justify-content: flex-end;
}

.result-action-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--primary-600);
    font-weight: 600;
    text-decoration: none;
    transition: all var(--transition-fast) var(--easing-standard);
}

.result-action-link:hover {
    color: var(--primary-700);
    text-decoration: none;
    transform: translateX(4px);
}

/* Pagination */
.search-pagination {
    display: flex;
    justify-content: center;
    margin-top: var(--spacing-2xl);
}

.search-pagination .page-numbers {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--gray-300);
    background: var(--surface);
    color: var(--gray-700);
    text-decoration: none;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast) var(--easing-standard);
}

.search-pagination .page-numbers:hover,
.search-pagination .page-numbers.current {
    background: var(--primary-500);
    border-color: var(--primary-500);
    color: white;
    text-decoration: none;
}

/* No Results */
.no-results,
.empty-search {
    text-align: center;
    padding: var(--spacing-4xl) 0;
}

.no-results-icon,
.empty-search-icon {
    color: var(--gray-300);
    margin-bottom: var(--spacing-xl);
}

.no-results-title,
.empty-search-title {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-lg);
}

.no-results-text,
.empty-search-text {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0 0 var(--spacing-2xl);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.search-suggestions,
.quick-search-categories {
    max-width: 500px;
    margin: 0 auto var(--spacing-2xl);
}

.search-suggestions h3,
.quick-search-categories h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-800);
    margin-bottom: var(--spacing-lg);
}

.suggestions-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.suggestions-list li {
    color: var(--gray-600);
    padding-left: var(--spacing-lg);
    position: relative;
}

.suggestions-list li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: var(--primary-500);
    font-weight: 700;
}

.popular-tags {
    display: flex;
    gap: var(--spacing-sm);
    justify-content: center;
    flex-wrap: wrap;
}

.popular-tag {
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    text-decoration: none;
    font-weight: 600;
    transition: all var(--transition-fast) var(--easing-standard);
}

.popular-tag:hover {
    background: var(--primary-500);
    color: white;
    text-decoration: none;
}

.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--spacing-lg);
}

.category-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-xl);
    background: var(--surface);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    text-decoration: none;
    color: var(--gray-700);
    transition: all var(--transition-fast) var(--easing-standard);
}

.category-card:hover {
    background: var(--primary-50);
    border-color: var(--primary-200);
    color: var(--primary-700);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    text-decoration: none;
}

/* Responsive Design */
@media (max-width: 768px) {
    .search-title {
        font-size: var(--text-2xl);
    }
    
    .search-input {
        font-size: var(--text-base);
        padding: var(--spacing-md);
    }
    
    .search-button {
        padding: var(--spacing-md);
    }
    
    .stock-results-grid {
        grid-template-columns: 1fr;
    }
    
    .stock-actions {
        flex-direction: column;
    }
    
    .category-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .popular-tags {
        justify-content: flex-start;
    }
}

/* Dark Mode */
[data-theme="dark"] .search-title,
[data-theme="dark"] .section-title,
[data-theme="dark"] .no-results-title,
[data-theme="dark"] .empty-search-title {
    color: var(--gray-100);
}

[data-theme="dark"] .search-input {
    background: var(--gray-800);
    border-color: var(--gray-600);
    color: var(--gray-200);
}

[data-theme="dark"] .content-result-card {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .result-link {
    color: var(--gray-200);
}

[data-theme="dark"] .category-card {
    background: var(--gray-800);
    border-color: var(--gray-700);
    color: var(--gray-300);
}

[data-theme="dark"] .category-card:hover {
    background: var(--gray-700);
    color: var(--primary-400);
}
</style>

<?php get_footer(); ?>