<?php
/**
 * The main template file
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="container">
    <div class="page-header animate-fade-up">
        <h1 class="page-title">
            <?php 
            if (is_home()) {
                bloginfo('name');
            } else {
                the_title();
            }
            ?>
        </h1>
        <?php if (is_home()) : ?>
            <p class="page-description">
                <?php bloginfo('description'); ?>
            </p>
        <?php endif; ?>
    </div>

    <div class="content-grid grid grid-auto-fit">
        <?php if (have_posts()) : ?>
            <?php while (have_posts()) : the_post(); ?>
                <article <?php post_class('card animate-scale-in'); ?> id="post-<?php the_ID(); ?>">
                    <?php if (has_post_thumbnail()) : ?>
                        <div class="card-thumbnail">
                            <?php the_post_thumbnail('large', ['class' => 'post-thumbnail']); ?>
                        </div>
                    <?php endif; ?>
                    
                    <div class="card-body">
                        <h2 class="card-title">
                            <a href="<?php the_permalink(); ?>" class="post-link">
                                <?php the_title(); ?>
                            </a>
                        </h2>
                        
                        <div class="post-meta flex items-center gap-md text-sm text-muted">
                            <time datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                                <?php echo rts_get_icon('calendar', ['width' => '16', 'height' => '16']); ?>
                                <?php the_date(); ?>
                            </time>
                            <span class="post-author">
                                <?php echo rts_get_icon('user', ['width' => '16', 'height' => '16']); ?>
                                <?php the_author(); ?>
                            </span>
                        </div>
                        
                        <div class="post-excerpt">
                            <?php the_excerpt(); ?>
                        </div>
                        
                        <div class="card-footer flex items-center justify-between">
                            <a href="<?php the_permalink(); ?>" class="btn btn-outline btn-sm">
                                <?php esc_html_e('Read More', 'retail-trade-scanner'); ?>
                                <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
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
            
            <!-- Pagination -->
            <div class="pagination-wrapper">
                <?php
                the_posts_pagination(array(
                    'prev_text' => rts_get_icon('chevron-left', ['width' => '16', 'height' => '16']) . ' ' . __('Previous', 'retail-trade-scanner'),
                    'next_text' => __('Next', 'retail-trade-scanner') . ' ' . rts_get_icon('chevron-right', ['width' => '16', 'height' => '16']),
                ));
                ?>
            </div>
            
        <?php else : ?>
            <div class="no-posts card text-center">
                <div class="card-body">
                    <?php echo rts_get_icon('search', ['width' => '48', 'height' => '48', 'class' => 'no-posts-icon text-muted']); ?>
                    <h2><?php esc_html_e('Nothing found', 'retail-trade-scanner'); ?></h2>
                    <p><?php esc_html_e('It seems we can\'t find what you\'re looking for. Perhaps searching can help.', 'retail-trade-scanner'); ?></p>
                    <div class="no-posts-search">
                        <?php get_search_form(); ?>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php
get_footer();