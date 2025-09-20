<?php
/**
 * Archive Template
 * Template for displaying archive pages (category, tag, date, author)
 */

get_header(); ?>

<div class="archive-wrapper">
    <div class="container">
        <header class="archive-header">
            <h1 class="archive-title">
                <?php
                if (is_category()) {
                    single_cat_title();
                } elseif (is_tag()) {
                    single_tag_title();
                } elseif (is_author()) {
                    printf(__('Posts by %s', 'stock-scanner'), get_the_author());
                } elseif (is_day()) {
                    printf(__('Daily Archives: %s', 'stock-scanner'), get_the_date());
                } elseif (is_month()) {
                    printf(__('Monthly Archives: %s', 'stock-scanner'), get_the_date('F Y'));
                } elseif (is_year()) {
                    printf(__('Yearly Archives: %s', 'stock-scanner'), get_the_date('Y'));
                } else {
                    _e('Archives', 'stock-scanner');
                }
                ?>
            </h1>
            
            <?php if (category_description() || tag_description()) : ?>
                <div class="archive-description">
                    <?php echo category_description() . tag_description(); ?>
                </div>
            <?php endif; ?>
        </header>

        <div class="archive-content">
            <?php if (have_posts()) : ?>
                <div class="posts-grid">
                    <?php while (have_posts()) : the_post(); ?>
                        <article id="post-<?php the_ID(); ?>" <?php post_class('archive-post'); ?>>
                            <?php if (has_post_thumbnail()) : ?>
                                <div class="post-thumbnail">
                                    <a href="<?php the_permalink(); ?>">
                                        <?php the_post_thumbnail('medium', array('class' => 'post-image')); ?>
                                    </a>
                                </div>
                            <?php endif; ?>
                            
                            <div class="post-content">
                                <div class="post-meta">
                                    <span class="post-date"><?php echo get_the_date(); ?></span>
                                    <span class="post-author">by <?php the_author(); ?></span>
                                </div>
                                
                                <h2 class="post-title">
                                    <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                </h2>
                                
                                <div class="post-excerpt">
                                    <?php 
                                    if (has_excerpt()) {
                                        the_excerpt();
                                    } else {
                                        echo wp_trim_words(get_the_content(), 30, '...');
                                    }
                                    ?>
                                </div>
                                
                                <div class="post-footer">
                                    <a href="<?php the_permalink(); ?>" class="read-more-btn">
                                        Read More →
                                    </a>
                                    
                                    <?php if (has_category()) : ?>
                                        <div class="post-categories">
                                            <?php the_category(', '); ?>
                                        </div>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </article>
                    <?php endwhile; ?>
                </div>

                <div class="archive-pagination">
                    <?php
                    the_posts_pagination(array(
                        'mid_size'  => 2,
                        'prev_text' => __('← Previous', 'stock-scanner'),
                        'next_text' => __('Next →', 'stock-scanner'),
                    ));
                    ?>
                </div>

            <?php else : ?>
                <div class="no-posts">
                    <div class="no-posts-icon">📝</div>
                    <h2>No posts found</h2>
                    <p>Sorry, no posts were found in this archive. Try searching for something else.</p>
                    <a href="<?php echo home_url(); ?>" class="btn btn-primary">
                        Back to Home
                    </a>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<style>
.archive-wrapper {
    padding: 2rem 0;
    background: var(--bg-secondary);
    min-height: 70vh;
}

.archive-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.archive-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.archive-description {
    color: var(--text-secondary);
    font-size: 1.125rem;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

.posts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.archive-post {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    transition: all var(--transition-normal);
    border: 1px solid var(--border-color);
}

.archive-post:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-5px);
}

.post-thumbnail {
    position: relative;
    overflow: hidden;
}

.post-image {
    width: 100%;
    height: 220px;
    object-fit: cover;
    transition: transform var(--transition-normal);
}

.archive-post:hover .post-image {
    transform: scale(1.05);
}

.post-content {
    padding: 1.5rem;
}

.post-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.post-meta span {
    padding: 0.25rem 0.5rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-sm);
}

.post-title {
    margin-bottom: 1rem;
}

.post-title a {
    color: var(--text-primary);
    text-decoration: none;
    font-size: 1.25rem;
    font-weight: 600;
    line-height: 1.3;
    transition: color var(--transition-normal);
}

.post-title a:hover {
    color: var(--primary-color);
}

.post-excerpt {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.post-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.read-more-btn {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all var(--transition-normal);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-sm);
    background: transparent;
}

.read-more-btn:hover {
    background: var(--primary-color);
    color: white;
}

.post-categories {
    font-size: 0.75rem;
}

.post-categories a {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color var(--transition-normal);
}

.post-categories a:hover {
    color: var(--primary-color);
}

.archive-pagination {
    text-align: center;
    margin-top: 3rem;
}

.page-numbers {
    display: inline-flex;
    gap: 0.5rem;
    align-items: center;
}

.page-numbers a,
.page-numbers span {
    padding: 0.75rem 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-decoration: none;
    transition: all var(--transition-normal);
}

.page-numbers a:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.page-numbers .current {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.no-posts {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.no-posts-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.no-posts h2 {
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.no-posts p {
    color: var(--text-secondary);
    margin-bottom: 2rem;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}

@media (max-width: 768px) {
    .archive-title {
        font-size: 2rem;
    }
    
    .posts-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .post-footer {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .archive-wrapper {
        padding: 1rem 0;
    }
    
    .archive-header {
        margin-bottom: 2rem;
        padding: 1.5rem;
    }
}
</style>

<?php get_footer(); ?>