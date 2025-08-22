<?php
/**
 * Search Results Template
 * Template for displaying search results
 */

get_header(); ?>

<div class="search-wrapper">
    <div class="container">
        <header class="search-header">
            <h1 class="search-title">
                <?php
                global $wp_query;
                $total_results = $wp_query->found_posts;
                
                if (have_posts()) {
                    printf(
                        _n(
                            '%1$s result found for "%2$s"',
                            '%1$s results found for "%2$s"',
                            $total_results,
                            'stock-scanner'
                        ),
                        number_format_i18n($total_results),
                        '<span class="search-query">' . get_search_query() . '</span>'
                    );
                } else {
                    printf(
                        __('No results found for "%s"', 'stock-scanner'),
                        '<span class="search-query">' . get_search_query() . '</span>'
                    );
                }
                ?>
            </h1>
            
            <div class="search-form-wrapper">
                <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
                    <label class="screen-reader-text"><?php _e('Search for:', 'stock-scanner'); ?></label>
                    <input type="search" class="search-field" placeholder="<?php echo esc_attr_x('Search...', 'placeholder', 'stock-scanner'); ?>" value="<?php echo get_search_query(); ?>" name="s" />
                    <button type="submit" class="search-submit">
                        <span>🔍</span>
                        <span class="button-text">Search</span>
                    </button>
                </form>
            </div>
        </header>

        <div class="search-content">
            <?php if (have_posts()) : ?>
                <div class="search-results">
                    <?php while (have_posts()) : the_post(); ?>
                        <article id="post-<?php the_ID(); ?>" <?php post_class('search-result'); ?>>
                            <div class="result-content">
                                <div class="result-meta">
                                    <span class="result-type">
                                        <?php 
                                        $post_type_obj = get_post_type_object(get_post_type());
                                        echo $post_type_obj->labels->singular_name;
                                        ?>
                                    </span>
                                    <span class="result-date"><?php echo get_the_date(); ?></span>
                                </div>
                                
                                <h2 class="result-title">
                                    <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                </h2>
                                
                                <div class="result-excerpt">
                                    <?php 
                                    $excerpt = get_the_excerpt();
                                    if (empty($excerpt)) {
                                        $content = get_the_content();
                                        $excerpt = wp_trim_words(strip_tags($content), 30, '...');
                                    }
                                    
                                    // Highlight search terms
                                    $search_query = get_search_query();
                                    if (!empty($search_query)) {
                                        $excerpt = preg_replace('/(' . preg_quote($search_query, '/') . ')/i', '<mark>$1</mark>', $excerpt);
                                    }
                                    
                                    echo $excerpt;
                                    ?>
                                </div>
                                
                                <div class="result-footer">
                                    <a href="<?php the_permalink(); ?>" class="result-link">
                                        Read More →
                                    </a>
                                    
                                    <div class="result-url">
                                        <?php echo esc_url(get_permalink()); ?>
                                    </div>
                                </div>
                            </div>
                        </article>
                    <?php endwhile; ?>
                </div>

                <div class="search-pagination">
                    <?php
                    the_posts_pagination(array(
                        'mid_size'  => 2,
                        'prev_text' => __('← Previous', 'stock-scanner'),
                        'next_text' => __('Next →', 'stock-scanner'),
                    ));
                    ?>
                </div>

            <?php else : ?>
                <div class="no-results">
                    <div class="no-results-icon">🔍</div>
                    <h2>No results found</h2>
                    <p>Sorry, we couldn't find any results for "<strong><?php echo get_search_query(); ?></strong>". Try adjusting your search terms or browse our popular content below.</p>
                    
                    <div class="search-suggestions">
                        <h3>Try searching for:</h3>
                        <div class="suggestion-tags">
                            <a href="<?php echo esc_url(home_url('?s=stock+analysis')); ?>" class="suggestion-tag">Stock Analysis</a>
                            <a href="<?php echo esc_url(home_url('?s=portfolio')); ?>" class="suggestion-tag">Portfolio</a>
                            <a href="<?php echo esc_url(home_url('?s=market+data')); ?>" class="suggestion-tag">Market Data</a>
                            <a href="<?php echo esc_url(home_url('?s=investing')); ?>" class="suggestion-tag">Investing</a>
                            <a href="<?php echo esc_url(home_url('?s=financial+news')); ?>" class="suggestion-tag">Financial News</a>
                        </div>
                    </div>
                    
                    <div class="popular-pages">
                        <h3>Popular Pages:</h3>
                        <div class="popular-links">
                            <a href="<?php echo home_url('/stock-screener/'); ?>" class="popular-link">Stock Screener</a>
                            <a href="<?php echo home_url('/market-overview/'); ?>" class="popular-link">Market Overview</a>
                            <a href="<?php echo home_url('/portfolio/'); ?>" class="popular-link">Portfolio Tracker</a>
                            <a href="<?php echo home_url('/premium-plans/'); ?>" class="popular-link">Premium Plans</a>
                        </div>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<style>
.search-wrapper {
    padding: 2rem 0;
    background: var(--bg-secondary);
    min-height: 70vh;
}

.search-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.search-title {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 2rem;
    line-height: 1.3;
}

.search-query {
    color: var(--primary-color);
    font-weight: 700;
}

.search-form-wrapper {
    max-width: 500px;
    margin: 0 auto;
}

.search-form {
    display: flex;
    gap: 0;
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: 0.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.search-field {
    flex: 1;
    padding: 1rem 1.5rem;
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 1rem;
    outline: none;
}

.search-field::placeholder {
    color: var(--text-secondary);
}

.search-submit {
    padding: 1rem 1.5rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all var(--transition-normal);
}

.search-submit:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.search-results {
    margin-bottom: 3rem;
}

.search-result {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
    transition: all var(--transition-normal);
}

.search-result:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.result-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.result-type {
    padding: 0.25rem 0.75rem;
    background: var(--primary-color);
    color: white;
    border-radius: var(--radius-sm);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.result-date {
    padding: 0.25rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-sm);
}

.result-title {
    margin-bottom: 1rem;
}

.result-title a {
    color: var(--text-primary);
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 600;
    line-height: 1.3;
    transition: color var(--transition-normal);
}

.result-title a:hover {
    color: var(--primary-color);
}

.result-excerpt {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.result-excerpt mark {
    background: rgba(var(--primary-color-rgb), 0.2);
    color: var(--primary-color);
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-weight: 600;
}

.result-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.result-link {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all var(--transition-normal);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-sm);
    background: transparent;
}

.result-link:hover {
    background: var(--primary-color);
    color: white;
}

.result-url {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-family: var(--font-mono);
}

.search-pagination {
    text-align: center;
    margin-top: 3rem;
}

.no-results {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.no-results-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.no-results h2 {
    color: var(--text-primary);
    margin-bottom: 1rem;
    font-size: 2rem;
}

.no-results p {
    color: var(--text-secondary);
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    font-size: 1.125rem;
    line-height: 1.6;
}

.search-suggestions,
.popular-pages {
    margin-bottom: 2rem;
}

.search-suggestions h3,
.popular-pages h3 {
    color: var(--text-primary);
    margin-bottom: 1rem;
    font-size: 1.25rem;
}

.suggestion-tags,
.popular-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
}

.suggestion-tag,
.popular-link {
    padding: 0.75rem 1.5rem;
    background: var(--bg-secondary);
    color: var(--text-primary);
    text-decoration: none;
    border-radius: var(--radius-lg);
    font-weight: 500;
    transition: all var(--transition-normal);
    border: 1px solid var(--border-color);
}

.suggestion-tag:hover,
.popular-link:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

@media (max-width: 768px) {
    .search-title {
        font-size: 1.5rem;
    }
    
    .search-form {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .result-footer {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .suggestion-tags,
    .popular-links {
        flex-direction: column;
        align-items: center;
    }
    
    .suggestion-tag,
    .popular-link {
        width: 100%;
        max-width: 300px;
        text-align: center;
    }
    
    .search-wrapper {
        padding: 1rem 0;
    }
    
    .search-header {
        margin-bottom: 2rem;
        padding: 1.5rem;
    }
    
    .search-result {
        padding: 1.5rem;
    }
}
</style>

<?php get_footer(); ?>