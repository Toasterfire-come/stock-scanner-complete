<?php
/**
 * The template for displaying all single posts
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="container">
    <?php while (have_posts()) : the_post(); ?>
        <article <?php post_class('single-post'); ?> id="post-<?php the_ID(); ?>">
            <header class="post-header animate-fade-up">
                <h1 class="post-title"><?php the_title(); ?></h1>
                
                <div class="post-meta flex items-center gap-lg text-sm text-muted">
                    <time datetime="<?php echo esc_attr(get_the_date('c')); ?>" class="post-date flex items-center gap-sm">
                        <?php echo rts_get_icon('calendar', ['width' => '16', 'height' => '16']); ?>
                        <?php the_date(); ?>
                    </time>
                    
                    <span class="post-author flex items-center gap-sm">
                        <?php echo rts_get_icon('user', ['width' => '16', 'height' => '16']); ?>
                        <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>">
                            <?php the_author(); ?>
                        </a>
                    </span>
                    
                    <?php if (has_category()) : ?>
                        <div class="post-categories flex items-center gap-sm">
                            <?php echo rts_get_icon('folder', ['width' => '16', 'height' => '16']); ?>
                            <?php the_category(', '); ?>
                        </div>
                    <?php endif; ?>
                    
                    <?php if (comments_open()) : ?>
                        <a href="#comments" class="comments-link flex items-center gap-sm">
                            <?php echo rts_get_icon('message-circle', ['width' => '16', 'height' => '16']); ?>
                            <?php comments_number('0 Comments', '1 Comment', '% Comments'); ?>
                        </a>
                    <?php endif; ?>
                </div>
            </header>

            <?php if (has_post_thumbnail()) : ?>
                <div class="post-thumbnail animate-scale-in">
                    <?php the_post_thumbnail('large', ['class' => 'featured-image']); ?>
                </div>
            <?php endif; ?>

            <div class="post-content-wrapper">
                <div class="entry-content">
                    <?php
                    the_content(sprintf(
                        wp_kses(
                            /* translators: %s: Name of current post. Only visible to screen readers */
                            __('Continue reading<span class="sr-only"> "%s"</span>', 'retail-trade-scanner'),
                            array(
                                'span' => array(
                                    'class' => array(),
                                ),
                            )
                        ),
                        wp_kses_post(get_the_title())
                    ));

                    wp_link_pages(array(
                        'before' => '<div class="page-links">' . esc_html__('Pages:', 'retail-trade-scanner'),
                        'after'  => '</div>',
                    ));
                    ?>
                </div>

                <?php if (has_tag()) : ?>
                    <div class="post-tags">
                        <h3><?php esc_html_e('Tags', 'retail-trade-scanner'); ?></h3>
                        <div class="tag-list">
                            <?php the_tags('<span class="tag-item">', '</span><span class="tag-item">', '</span>'); ?>
                        </div>
                    </div>
                <?php endif; ?>

                <!-- Author Bio -->
                <?php
                $author_bio = get_the_author_meta('description');
                if ($author_bio) :
                ?>
                    <div class="author-bio card">
                        <div class="card-body flex gap-lg">
                            <div class="author-avatar">
                                <?php echo get_avatar(get_the_author_meta('ID'), 80, '', '', ['class' => 'avatar']); ?>
                            </div>
                            <div class="author-info">
                                <h3 class="author-name">
                                    <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>">
                                        <?php the_author(); ?>
                                    </a>
                                </h3>
                                <p class="author-description"><?php echo esc_html($author_bio); ?></p>
                                <div class="author-links">
                                    <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" class="btn btn-outline btn-sm">
                                        <?php esc_html_e('View All Posts', 'retail-trade-scanner'); ?>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                <?php endif; ?>

                <!-- Post Navigation -->
                <nav class="post-navigation" role="navigation" aria-labelledby="post-navigation">
                    <h2 id="post-navigation" class="sr-only"><?php esc_html_e('Post navigation', 'retail-trade-scanner'); ?></h2>
                    <div class="nav-links grid grid-2 gap-lg">
                        <?php
                        $prev_post = get_previous_post();
                        $next_post = get_next_post();
                        ?>
                        
                        <?php if ($prev_post) : ?>
                            <div class="nav-previous">
                                <a href="<?php echo esc_url(get_permalink($prev_post)); ?>" class="nav-link card">
                                    <div class="card-body">
                                        <div class="nav-direction flex items-center gap-sm text-sm text-muted">
                                            <?php echo rts_get_icon('chevron-left', ['width' => '16', 'height' => '16']); ?>
                                            <?php esc_html_e('Previous Post', 'retail-trade-scanner'); ?>
                                        </div>
                                        <h3 class="nav-title"><?php echo esc_html(get_the_title($prev_post)); ?></h3>
                                    </div>
                                </a>
                            </div>
                        <?php endif; ?>

                        <?php if ($next_post) : ?>
                            <div class="nav-next">
                                <a href="<?php echo esc_url(get_permalink($next_post)); ?>" class="nav-link card">
                                    <div class="card-body text-right">
                                        <div class="nav-direction flex items-center justify-end gap-sm text-sm text-muted">
                                            <?php esc_html_e('Next Post', 'retail-trade-scanner'); ?>
                                            <?php echo rts_get_icon('chevron-right', ['width' => '16', 'height' => '16']); ?>
                                        </div>
                                        <h3 class="nav-title"><?php echo esc_html(get_the_title($next_post)); ?></h3>
                                    </div>
                                </a>
                            </div>
                        <?php endif; ?>
                    </div>
                </nav>

                <!-- Related Posts -->
                <?php
                $related_posts = get_posts(array(
                    'category__in' => wp_get_post_categories($post->ID),
                    'numberposts' => 3,
                    'post__not_in' => array($post->ID),
                ));

                if ($related_posts) :
                ?>
                    <section class="related-posts">
                        <h2><?php esc_html_e('Related Posts', 'retail-trade-scanner'); ?></h2>
                        <div class="related-posts-grid grid grid-3 gap-lg">
                            <?php foreach ($related_posts as $related_post) : ?>
                                <article class="related-post card">
                                    <?php if (has_post_thumbnail($related_post->ID)) : ?>
                                        <div class="card-thumbnail">
                                            <a href="<?php echo esc_url(get_permalink($related_post)); ?>">
                                                <?php echo get_the_post_thumbnail($related_post->ID, 'medium', ['class' => 'related-post-thumbnail']); ?>
                                            </a>
                                        </div>
                                    <?php endif; ?>
                                    
                                    <div class="card-body">
                                        <h3 class="card-title">
                                            <a href="<?php echo esc_url(get_permalink($related_post)); ?>">
                                                <?php echo esc_html(get_the_title($related_post)); ?>
                                            </a>
                                        </h3>
                                        <p class="post-excerpt">
                                            <?php echo esc_html(wp_trim_words(get_the_excerpt($related_post), 15)); ?>
                                        </p>
                                        <div class="card-footer">
                                            <time datetime="<?php echo esc_attr(get_the_date('c', $related_post)); ?>" class="post-date text-sm text-muted">
                                                <?php echo esc_html(get_the_date('', $related_post)); ?>
                                            </time>
                                        </div>
                                    </div>
                                </article>
                            <?php endforeach; ?>
                        </div>
                    </section>
                <?php endif; ?>

                <!-- Comments -->
                <?php if (comments_open() || get_comments_number()) : ?>
                    <div class="comments-section">
                        <?php comments_template(); ?>
                    </div>
                <?php endif; ?>
            </div>
        </article>
    <?php endwhile; ?>
</div>

<?php
get_footer();