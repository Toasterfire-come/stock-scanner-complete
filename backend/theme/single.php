<?php
/**
 * Single Post Template
 * Template for displaying single blog posts
 */

get_header(); ?>

<div class="single-post-wrapper">
    <div class="container">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class('single-post'); ?>>
                <header class="post-header">
                    <div class="post-meta">
                        <span class="post-date"><?php echo get_the_date(); ?></span>
                        <span class="post-author">by <?php the_author(); ?></span>
                        <?php if (has_category()) : ?>
                            <span class="post-categories"><?php the_category(', '); ?></span>
                        <?php endif; ?>
                    </div>
                    
                    <h1 class="post-title"><?php the_title(); ?></h1>
                    
                    <?php if (has_post_thumbnail()) : ?>
                        <div class="post-thumbnail">
                            <?php the_post_thumbnail('large', array('class' => 'featured-image')); ?>
                        </div>
                    <?php endif; ?>
                </header>

                <div class="post-content">
                    <?php the_content(); ?>
                    
                    <?php
                    wp_link_pages(array(
                        'before' => '<div class="page-links">',
                        'after'  => '</div>',
                        'link_before' => '<span class="page-number">',
                        'link_after'  => '</span>',
                    ));
                    ?>
                </div>

                <footer class="post-footer">
                    <?php if (has_tag()) : ?>
                        <div class="post-tags">
                            <strong>Tags:</strong> <?php the_tags('', ', ', ''); ?>
                        </div>
                    <?php endif; ?>
                    
                    <div class="post-navigation">
                        <?php
                        $prev_post = get_previous_post();
                        $next_post = get_next_post();
                        ?>
                        
                        <?php if ($prev_post) : ?>
                            <div class="nav-previous">
                                <a href="<?php echo get_permalink($prev_post); ?>" class="nav-link">
                                    <span class="nav-direction">← Previous</span>
                                    <span class="nav-title"><?php echo get_the_title($prev_post); ?></span>
                                </a>
                            </div>
                        <?php endif; ?>
                        
                        <?php if ($next_post) : ?>
                            <div class="nav-next">
                                <a href="<?php echo get_permalink($next_post); ?>" class="nav-link">
                                    <span class="nav-direction">Next →</span>
                                    <span class="nav-title"><?php echo get_the_title($next_post); ?></span>
                                </a>
                            </div>
                        <?php endif; ?>
                    </div>
                </footer>
            </article>

            <?php
            // If comments are open or we have at least one comment, load up the comment template.
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;
            ?>

        <?php endwhile; endif; ?>
    </div>
</div>

<style>
.single-post-wrapper {
    padding: 2rem 0;
    background: var(--bg-primary);
}

.single-post {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: 2rem;
    margin-bottom: 2rem;
}

.post-header {
    margin-bottom: 2rem;
    text-align: center;
}

.post-meta {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.post-meta span {
    padding: 0.25rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-sm);
}

.post-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    line-height: 1.2;
}

.post-thumbnail {
    margin: 2rem 0;
}

.featured-image {
    width: 100%;
    height: auto;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}

.post-content {
    line-height: 1.7;
    color: var(--text-primary);
    margin-bottom: 2rem;
}

.post-content h2,
.post-content h3,
.post-content h4 {
    margin: 2rem 0 1rem;
    color: var(--text-primary);
}

.post-content p {
    margin-bottom: 1.5rem;
}

.post-content img {
    max-width: 100%;
    height: auto;
    border-radius: var(--radius-md);
    margin: 1rem 0;
}

.post-footer {
    border-top: 1px solid var(--border-color);
    padding-top: 2rem;
}

.post-tags {
    margin-bottom: 2rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    font-size: 0.875rem;
}

.post-navigation {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.nav-link {
    display: block;
    padding: 1.5rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    text-decoration: none;
    transition: all var(--transition-normal);
    border: 1px solid var(--border-color);
}

.nav-link:hover {
    background: var(--primary-color);
    color: white;
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.nav-direction {
    display: block;
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.nav-title {
    display: block;
    font-weight: 600;
    color: var(--text-primary);
}

.nav-link:hover .nav-direction,
.nav-link:hover .nav-title {
    color: white;
}

.nav-next {
    text-align: right;
}

@media (max-width: 768px) {
    .post-title {
        font-size: 2rem;
    }
    
    .post-meta {
        flex-direction: column;
        gap: 0.5rem;
        align-items: center;
    }
    
    .post-navigation {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .nav-next {
        text-align: left;
    }
    
    .single-post {
        padding: 1.5rem;
    }
}
</style>

<?php get_footer(); ?>